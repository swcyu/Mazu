from pyspark.sql.functions import *
from pyspark.sql.types import *
import requests
from datetime import datetime

time = datetime.now()
now = time.strftime('%Y%m%d')

##spark-submit 실행파일시
from pyspark.sql import SparkSession
spark =SparkSession.builder.getOrCreate()

# 하둡에서 데이터 가져오기
df_pre = spark.read.format("csv").option("header", "true").option("multiline", "true").option("quote", "\"").option(
    "escape", "\"").load(f"yogi6/raw_data/crawling/{now}/MMCA.csv")
#df_past = spark.read.format("csv").option("header", "true").option("multiline", "true").option("quote", "\"").option(
#    "escape", "\"").load("yogi6/raw_data/crawling/init/mmca_past.csv")

'''
예전꺼
df_pre = spark.read.format("csv").option("header", "true").option("multiline", "true").option("quote", "\"").option(
    "escape", "\"").load("yogi6/raw_data/crawling/mmca/init/mmca_pre.csv")
df_past = spark.read.format("csv").option("header", "true").option("multiline", "true").option("quote", "\"").option(
    "escape", "\"").load("yogi6/raw_data/crawling/mmca/init/mmca_past.csv")
'''
# 사용할 칼럼만 선택
df_pre = df_pre.select('exhibition_id','exhibition_name', 'poster_link', 'exhibition_description', 'exhibition_period', 'exhibition_place')
#df_past = df_past.select('exhibition_name', 'poster_link', 'exhibition_description', 'exhibition_period', 'exhibition_place')

df = df_pre.dropDuplicates(['exhibition_name'])\
    .dropna('any', None, ['exhibition_name', 'exhibition_period'])\
    .withColumn('start_period', to_date(substring(trim(split('exhibition_period', '~').getItem(0)), 1, 10), 'yyyy-MM-dd'))\
    .withColumn('end_period', to_date(substring(trim(split('exhibition_period', '~').getItem(1)), 1, 10), 'yyyy-MM-dd')).drop('exhibition_period')\
    .filter(col("start_period") > lit("2015-12-31"))
df2 = df.withColumn("place", when(df.exhibition_place.contains("서울"), "국립현대미술관 서울관")
                .when(df.exhibition_place.contains("청주"), "국립현대미술관 청주")
                .when(df.exhibition_place.contains("과천"),"국립현대미술관 과천관")
                .when(df.exhibition_place.contains("덕수궁"), "국립현대미술관 덕수궁관")
                .when(df.exhibition_place.contains("어린이미술관"), "국립현대미술관 어린이미술관")
                .when(df.exhibition_place.contains("창동"), "국립현대미술관 창동레지던시")
                .when(df.exhibition_place.contains("고양"), "국립현대미술관 고양레지던시")
                .otherwise(df.exhibition_place))

##파일 저장##
# 분석, 리뷰크롤링용 csv파일
#pd_df = df2.toPandas()
#pd_df.to_csv('~/yogi6/ds/file/mmca.csv', encoding="utf-8-sig")

##df_final생성##
target_list = df2.select(col('place')).collect()
place_list = list(set(map(lambda x: x[0], target_list)))

address_list = []
place_name_list = []

# 도로주소를 알기위한 api호출 - 도로명 주소, 장소명 가져오기
for search_place in place_list:
    url = f"https://dapi.kakao.com/v2/local/search/keyword.json?query={search_place}"
    kakao_key = "eeb4d25bd0990160503da341e8678475"
    result = requests.get(url, headers={"Authorization": f"KakaoAK {kakao_key}"})
    json_obj = result.json()
    # print(json_obj)
    # 검색결과가 없으면 ''을 값으로 넣는다.
    if json_obj['meta']['total_count'] == 0:
        address = ''
        place_name = search_place
    else:
        address = json_obj['documents'][0]['road_address_name']
        place_check = json_obj['documents'][0]['place_name']
        if place_check == '':
            place_name = search_place
        else:
            place_name = place_check

    address_list.append(address)
    place_name_list.append(place_name)

col_list = ['place', 'address', 'x', 'y', 'post_num', 'place_name']
row_list = []

# place_df 만들기위한 api호출
for idx, search_address in enumerate(address_list):
    value_list = []
    if search_address == '':
        place = place_list[idx]
        place_name = place_name_list[idx]
        address = ''
        x = ''
        y = ''
        post_num = ''
    else:
        url = f"https://dapi.kakao.com/v2/local/search/address.json?query={search_address}"
        kakao_key = "eeb4d25bd0990160503da341e8678475"
        result = requests.get(url, headers={"Authorization": f"KakaoAK {kakao_key}"})
        json_obj = result.json()
        # print(json_obj)

        place = place_list[idx]
        place_name = place_name_list[idx]
        address = search_address
        x = json_obj['documents'][0]['x']
        y = json_obj['documents'][0]['y']
        post_num = json_obj['documents'][0]['road_address']['zone_no']

    value_list.append(place)
    value_list.append(address)
    value_list.append(x)
    value_list.append(y)
    value_list.append(post_num)
    value_list.append(place_name)
    row_list.append(value_list)

# 새로운 place_df생성
place_df = spark.createDataFrame(row_list, schema=col_list)

#최종 결과물
df_final = df2.join(place_df, df2.place == place_df.place,"left")\
    .drop(place_df.place)\
    .orderBy(col('start_period').desc())\
    .drop(col('place_name'))


#df_final.show(df_final.count())
#print(df_final.printSchema())


#배포용 파일
#df_final.write.format('parquet').mode('overwrite').save("file:///home/ubuntu/yogi6/tr_data/crawling/init/mmca.parquet")
#df_final.write.format('parquet').mode('overwrite').save("file:///home/ubuntu/yogi6/tr_data/crawling/mmca/init/mmca.parquet")

#1차 가공된 파일
#df_final.write.format('parquet').mode('overwrite').save("hdfs:///user/ubuntu/yogi6/tr_data/crawling/init/mmca.parquet")
df_final.write.format('parquet').mode('overwrite').save(f"hdfs:///user/ubuntu/yogi6/tr_data/crawling/{now}/mmca.parquet")

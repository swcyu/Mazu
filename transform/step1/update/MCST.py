from pyspark.sql.functions import *
from pyspark.sql.types import *
import requests
from datetime import datetime

time = datetime.now()
now = time.strftime('%Y%m%d')

##spark-submit 실행파일시
from pyspark.sql import SparkSession
spark = SparkSession.builder.getOrCreate()

# 하둡에서 데이터 가져오기
df1 = spark.read.format("csv").option("header","true").option("multiline","true").option("quote", "\"").option("escape","\"").load(f"hdfs:///user/ubuntu/yogi6/raw_data/crawling/{now}/MCST.csv")
#df_2 = spark.read.format("csv").option("header","true").option("multiline","true").option("quote", "\"").option("escape","\"").load("yogi6/raw_data/crawling/init/mcst_2.csv")

# 사용할 칼럼만 선택
df2 = df1.select('exhibition_id', 'exhibition_name', 'poster_link', 'exhibition_description', 'exhibition_period', 'exhibition_place')
#df_2 = df_2.select('exhibition_name', 'poster_link', 'exhibition_description', 'exhibition_period', 'exhibition_place')

df = df2\
    .dropDuplicates(['exhibition_name'])\
    .dropna('any', None, ['exhibition_name', 'exhibition_period'])\

# 'exhibiton_period' 가공
period1 = df.withColumn('start_period', split('exhibition_period', '~').getItem(0))\
    .withColumn('end_period', split('exhibition_period', '~').getItem(1)).drop('exhibition_period')
period2 = period1.withColumn('start_period',regexp_replace('start_period', '[.]', ''))\
    .withColumn('end_period',regexp_replace('end_period', '[.]', ''))
period3 = period2.withColumn('start_period',regexp_replace('start_period', ' ', '-'))\
    .withColumn('end_period',regexp_replace('end_period', ' ', '-'))
period4 = period3.withColumn("start_period",from_unixtime(unix_timestamp(col("start_period"),'yyyy-M-d'),'yyyy-MM-dd'))\
    .withColumn("end_period",from_unixtime(unix_timestamp(col("end_period"),'yyyy-M-d'),'yyyy-MM-dd'))\
    .filter(year(col('start_period')) > 2015)
# 'exhibition_place' 가공
final = period4.withColumn('place', regexp_replace('exhibition_place', ' [|]', ''))\
    .withColumn('place', split('place', '[(]').getItem(0))\
    .withColumn('exhibition_description', regexp_replace(col('exhibition_description'), '전시소개', ''))

#pd_df = final.toPandas()

##파일 저장##
# 분석, 리뷰크롤링용 csv파일
#pd_df.to_csv('~/yogi6/ds/file/mcst.csv', encoding="utf-8-sig")

##df_final생성##
target_list = final.select(col('place')).collect()
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
    if json_obj['meta']['total_count'] != 0:
        address = json_obj['documents'][0]['road_address_name']
        place_check = json_obj['documents'][0]['place_name']
        if place_check == '':
            place_name = search_place
        else:
            place_name = place_check
    else:
        # 검색 후 없으면 맨 앞 두글자 + 공백 제외하고 검색
        keyword = search_place[3:]
        url = f"https://dapi.kakao.com/v2/local/search/keyword.json?query={keyword}"
        result = requests.get(url, headers={"Authorization": f"KakaoAK {kakao_key}"})
        json_obj = result.json()

        if json_obj['meta']['total_count'] != 0:
            address = json_obj['documents'][0]['road_address_name']
            place_check = json_obj['documents'][0]['place_name']
            if place_check == '':
                place_name = search_place
            else:
                place_name = place_check
        # 또 결과 없으면 맨 앞 두단어만 검색
        else:
            keyword = search_place.split(' ')[:2]
            url = f"https://dapi.kakao.com/v2/local/search/keyword.json?query={keyword}"
            result = requests.get(url, headers={"Authorization": f"KakaoAK {kakao_key}"})
            json_obj = result.json()

            if json_obj['meta']['total_count'] != 0:
                address = json_obj['documents'][0]['road_address_name']
                place_check = json_obj['documents'][0]['place_name']
                if place_check == '':
                    place_name = search_place
                else:
                    place_name = place_check
            else:
                address = ''
                place_name = search_place

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
df_final = final.join(place_df, final.place == place_df.place,"left")\
    .drop(place_df.place)\
    .orderBy(col('start_period').desc())\
    .drop(col('place_name'))
    
#pd_df = df_final.toPandas()
#pd_df.to_csv('~/yogi6/ds/file/MCST.csv', encoding="utf-8-sig", index=False)

#배포용 파일
##df_final.write.format('parquet').mode('overwrite').save("file:///home/ubuntu/yogi6/tr_data/crawling/mcst/init/mmca.parquet")
#df_final.write.format('parquet').mode('overwrite').save(f"file:///home/ubuntu/yogi6/tr_data/crawling/{now}/mcst.parquet")
#1차 가공된 파일
##df_final.write.format('parquet').mode('overwrite').save("hdfs:///user/ubuntu/yogi6/tr_data/crawling/mcst/init/mmca.parquet")
df_final.write.format('parquet').mode('overwrite').save(f"hdfs:///user/ubuntu/yogi6/tr_data/crawling/{now}/mcst.parquet")
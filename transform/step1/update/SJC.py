# sjc(세종문화회관)

from pyspark.sql.functions import *
from pyspark.sql.types import *
import requests
import json
from pprint import pprint
import pandas as pd
from datetime import datetime

time = datetime.now()
now = time.strftime('%Y%m%d')

##spark-submit 실행파일시
from pyspark.sql import SparkSession
spark =SparkSession.builder.getOrCreate()
sjc_csv = spark.read.format("csv").option("header", "true"). \
    option("multiline", "true").option("quote", "\"").option("escape", "\"") \
    .load(f"yogi6/raw_data/crawling/{now}/SJC.csv")
'''
sjc_csv = spark.read.format("csv").option("header", "true"). \
    option("multiline", "true").option("quote", "\"").option("escape", "\"") \
    .load("yogi6/raw_data/crawling/sjc/init/sjc_all.csv")
'''

sjc = sjc_csv.dropna('any', None, ['exhibition_name', 'exhibition_period'])\
    .withColumn('start_period', split(col('exhibition_period'), '~').getItem(0)) \
    .withColumn('end_period', split(col('exhibition_period'), '~').getItem(1)) \
    .withColumn('start_period', regexp_replace('start_period', '\D', '')) \
    .withColumn('end_period', regexp_replace('end_period', '\D', '')) \
    .withColumn('start_period', to_date(col('start_period'), 'yyyyMMdd')) \
    .withColumn('end_period', to_date(col('start_period'), 'yyyyMMdd')) \
    .filter(col("start_period") > lit("2015-12-31")).drop(col('exhibition_period')) \
    .filter(col('exhibition_place') != '2017').filter(col('exhibition_place') != '1010') \
    .filter(col('exhibition_place') != '8016').withColumn("place", when(col('exhibition_place') \
                                                                        .contains("세종"), "세종문화회관").when(
    col('exhibition_place').contains("야외전시"), "세종문화회관") \
                                                          .when(col('exhibition_place').contains("광화랑"), "세종문화회관").when(
    col('exhibition_place') \
    .contains("충무공"), "세종문화회관").when(col('exhibition_place') \
                                     .contains("컨서트홀"), "꿈의숲아트센터").when(col('exhibition_place') \
                                                                        .contains("퍼포먼스홀"), "꿈의숲아트센터").when(
    col('exhibition_place') \
    .contains("드림갤러리"), "꿈의숲아트센터").when(col('exhibition_place') \
                                        .contains("상상톡톡미술관"), "꿈의숲아트센터").when(col('exhibition_place') \
                                                                              .contains("전망대"), "꿈의숲아트센터").when(
    col('exhibition_place') \
    .contains("기타"), "꿈의숲아트센터").otherwise(col('exhibition_place'))) \
    .drop_duplicates(['exhibition_name'])

# 분석용 CSV파일 저장
#pd_df = sjc.toPandas()
#pd_df.to_csv('~/yogi6/ds/file/sjc.csv', encoding="utf-8-sig")

target_list = sjc.select(col('place')).collect()
place_list = list(set(map(lambda x: x[0], target_list)))

address_list = []

for place in place_list:
    value_list = []
    url = f"https://dapi.kakao.com/v2/local/search/keyword.json?query={place}"
    kakao_key = "eeb4d25bd0990160503da341e8678475"
    result = requests.get(url, headers={"Authorization": f"KakaoAK {kakao_key}"})
    json_obj = result.json()

    try:
        address = json_obj['documents'][0]['road_address_name']
    except:
        address = None

    address_list.append(address)
# print(len(address_list)) : 2 sjc.count() : 410

col_list = ['place', 'address', 'x', 'y', 'post_num']
row_list = []
# place_df 만들기위한 api호출(도로명검색)
for idx, search_address in enumerate(address_list):
    value_list = []
    url = f"https://dapi.kakao.com/v2/local/search/address.json?query={search_address}"
    kakao_key = "eeb4d25bd0990160503da341e8678475"
    result = requests.get(url, headers={"Authorization": f"KakaoAK {kakao_key}"})
    json_obj = result.json()

    try:
        place = place_list[idx]
        address = search_address
        x = json_obj['documents'][0]['x']
        y = json_obj['documents'][0]['y']
        post_num = json_obj['documents'][0]['road_address']['zone_no']
    except:
        place = place_list[idx]
        address = search_address
        x = None
        y = None
        post_num = None

    value_list.append(place)
    value_list.append(address)
    value_list.append(x)
    value_list.append(y)
    value_list.append(post_num)
    row_list.append(value_list)
# print(len(row_list)) : 2

# 새로운 place_df생성
place_df = spark.createDataFrame(row_list, schema=col_list)

df_final = sjc.join(place_df, sjc.place == place_df.place, 'left') \
    .drop(place_df.place).orderBy(col('start_period').desc())


#df_final.show(df_final.count())
#print(df_final.printSchema())

# df_final.count() : 410

# 배포용 파일
#df_final.write.format('parquet').mode("overwrite").save("file:///home/ubuntu/yogi6/tr_data/crawling/sjc/init/sjc.parquet")
#df_final.write.format('parquet').mode("overwrite").save("file:///home/ubuntu/yogi6/tr_data/crawling/init/sjc.parquet")
# 1차 가공된 파일
#df_final.write.format('parquet').mode("overwrite").save("hdfs:///user/ubuntu/yogi6/tr_data/crawling/sjc/init/sjc.parquet")
df_final.write.format('parquet').mode("overwrite").save(f"hdfs:///user/ubuntu/yogi6/tr_data/crawling/{now}/sjc.parquet")
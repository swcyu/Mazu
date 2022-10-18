# Sema (서울시립 미술관)

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

#sema_past_csv = spark.read.format("csv").option("header", "true"). \
#    option("multiline", "true").option("quote", "\"").option("escape", "\"") \
#    .load("yogi6/raw_data/crawling/init/sema_past.csv")
sema_pre_csv = spark.read.format("csv").option("header", "true"). \
    option("multiline", "true").option("quote", "\"").option("escape", "\"") \
    .load(f"yogi6/raw_data/crawling/{now}/SEMA.csv")
'''
sema_past_csv = spark.read.format("csv").option("header", "true"). \
    option("multiline", "true").option("quote", "\"").option("escape", "\"") \
    .load("yogi6/raw_data/crawling/sema/init/sema_past.csv")
sema_pre_csv = spark.read.format("csv").option("header", "true"). \
    option("multiline", "true").option("quote", "\"").option("escape", "\"") \
    .load("yogi6/raw_data/crawling/sema/init/sema_pre.csv")
'''

'''
sema_past = sema_past_csv\
    .dropna('any', None, ['exhibition_name', 'exhibition_period'])\
    .withColumn('start_period', split(col('exhibition_period'), '~').getItem(0)) \
    .withColumn('end_period', split(col('exhibition_period'), '~').getItem(1)) \
    .withColumn('start_period', regexp_replace('start_period', '\D', '')) \
    .withColumn('end_period', regexp_replace('end_period', '\D', '')). \
    withColumn('start_period', to_date(col('start_period'), 'yyyyMMdd')). \
    withColumn('end_period', to_date(col('start_period'), 'yyyyMMdd')). \
    filter(col("start_period") > lit("2015-12-31")).drop(col('exhibition_period')). \
    withColumn('exhibition_place', regexp_replace(col('exhibition_place'), '온라인, ', ''))
'''
sema_pre = sema_pre_csv.dropna(subset=['exhibition_name', 'exhibition_period']) \
    .withColumn('exhibition_period', regexp_replace(col('exhibition_period'), "상시", "2016/01/01~2999/12/31")) \
    .withColumn('start_period', split(col('exhibition_period'), '~').getItem(0)) \
    .withColumn('end_period', split(col('exhibition_period'), '~').getItem(1)) \
    .withColumn('start_period', regexp_replace('start_period', '\D', '')) \
    .withColumn('end_period', regexp_replace('end_period', '\D', '')) \
    .withColumn('start_period', to_date(col('start_period'), 'yyyyMMdd')) \
    .withColumn('end_period', to_date(col('start_period'), 'yyyyMMdd')) \
    .filter(col("start_period") > lit("2015-12-31")).drop(col('exhibition_period')) \
    .withColumn('exhibition_place', regexp_replace(col('exhibition_place'), '온라인, ', ''))

sema_all = sema_pre.filter(col('exhibition_place') != '외부장소')\
    .filter(col('exhibition_place') != '예술공간+의식주 (서울시 마포구 월드컵로16길 52-19)')\
    .filter(col('exhibition_place') != '대만 슈에슈에재단 백색공간').drop(col('_c0'))\
    .withColumn('exhibition_place', split('exhibition_place', '[(]').getItem(0))\
    .withColumn('exhibition_place', split('exhibition_place', '[,]').getItem(0))\
    .withColumn('exhibition_place', trim(col('exhibition_place')))\
    .filter(col('exhibition_place') != '문래동 상상채굴단').filter(col('exhibition_place') != '오브제트에이')\
    .filter(col('exhibition_place') != '갤러리 모디움').withColumn("place", when(col('exhibition_place')\
    .contains("기타 서교예술실험센터"), "서교예술실험센터").when(col('exhibition_place')\
    .contains("디플로허"), "드플로허").when(col('exhibition_place')\
    .contains("임시공간 구시가지"), "임시공간").when(col('exhibition_place')\
    .contains("갤러리 라메르"), "갤러리 라메르").when(col('exhibition_place')\
    .contains("갤러리 드플로허"), "드플로허").otherwise(col('exhibition_place')))\
    .withColumn('exhibition_description', regexp_replace(col('exhibition_description'), '맑은 ', ''))\
    .withColumn('exhibition_description', regexp_replace(col('exhibition_description'), '맑은', ''))\
    .withColumn('exhibition_description', regexp_replace(col('exhibition_description'), '고딕 ', ''))\
    .withColumn('exhibition_description', regexp_replace(col('exhibition_description'), '고딕', ''))

# 분석용 CSV파일 저장
#pd_df = sema_all.toPandas()
#pd_df.to_csv('~/yogi6/ds/file/sema.csv', encoding="utf-8-sig")

target_list = sema_all.select(col('place')).collect()
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
# print(len(address_list)) : 2 sema_all.count() : 348

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

df_final = sema_all.join(place_df, sema_all.place == place_df.place, 'left') \
    .drop(place_df.place).orderBy(col('start_period').desc()) \

#df_final.show(df_final.count())
#print(df_final.printSchema())


# df_final.count() : 348

# 배포용 파일
#df_final.write.format('parquet').mode("overwrite").save("file:///home/ubuntu/yogi6/tr_data/crawling/init/sema.parquet")

df_final.write.format('parquet').mode("overwrite").save(f"hdfs:///user/ubuntu/yogi6/tr_data/crawling/{now}/sema.parquet")
# 인덱스(c0) 컬럼이 제일 오른쪽에 있어요!

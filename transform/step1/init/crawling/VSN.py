from pyspark.sql.functions import col
from pyspark.sql.functions import to_date
from pyspark.sql.functions import when
from pyspark.sql.functions import substring
from pyspark.sql.functions import split
from pyspark.sql.functions import trim
from pyspark.sql.functions import monotonically_increasing_id
import pandas as pd
import json
from pprint import pprint
import requests

##spark-submit 실행파일시##
from pyspark.sql import SparkSession
spark =SparkSession.builder.getOrCreate()


# 하둡에서 파일 불러오기
df_pre = spark.read.format("csv").option("header", "true").option("multiline", "true").option("quote", "\"").option(
    "escape", "\"").load("yogi6/raw_data/crawling/init/vsn_pre.csv")
df_past = spark.read.format("csv").option("header", "true").option("multiline", "true").option("quote", "\"").option(
    "escape", "\"").load("yogi6/raw_data/crawling/init/vsn_past.csv")

'''
df_pre = spark.read.format("csv").option("header", "true").option("multiline", "true").option("quote", "\"").option(
    "escape", "\"").load("yogi6/raw_data/crawling/vsn/init/vsn_pre.csv")
df_past = spark.read.format("csv").option("header", "true").option("multiline", "true").option("quote", "\"").option(
    "escape", "\"").load("yogi6/raw_data/crawling/vsn/init/vsn_past.csv")
'''

df = df_pre.union(df_past) \
    .dropDuplicates(['exhibition_name']) \
    .withColumn('exhibition_period',
                when(col('exhibition_period').substr(1, 4) >= '2016', col('exhibition_period')).otherwise(None)) \
    .dropna('any', None, ['exhibition_name', 'exhibition_period'])\
    .withColumn('start_period',
                to_date(substring(trim(split('exhibition_period', '~').getItem(0)), 1, 10), 'yyyy.MM.dd')) \
    .withColumn('end_period', to_date(substring(trim(split('exhibition_period', '~').getItem(1)), 1, 10), 'yyyy.MM.dd')) \
    .drop(col('exhibition_period')).drop(col('_c0')) \
    .withColumn('place', split(col('exhibition_place'), '\xa0\xa0').getItem(1)) \
    .orderBy(col('start_period').desc())
# .coalesce(1).withColumn('_c0', monotonically_increasing_id())

pd_df = df.toPandas()

# 분석, 리뷰크롤링용 csv파일 저장
#pd_df.to_csv('~/yogi6/ds/file/vsn.csv', encoding="utf-8-sig")

##df_final생성##
# 카카오api에 검색할 place뽑기
target_list = df.select(col('place')).collect()
place_list = list(map(lambda x: x[0], target_list))

col_list = ['join_place', 'place', 'address', 'x', 'y', 'post_num']
row_list = []

for search_place in place_list:
    value_list = []
    # 카카오api호출
    url = f"https://dapi.kakao.com/v2/local/search/address.json?query={search_place}"
    kakao_key = "eeb4d25bd0990160503da341e8678475"
    result = requests.get(url, headers={"Authorization": f"KakaoAK {kakao_key}"})
    json_obj = result.json()

    try:
        join_place = search_place
        if json_obj['documents'][0]['road_address']['building_name']:
            place = json_obj['documents'][0]['road_address']['building_name']
        else:
            place = search_place
        address = json_obj['documents'][0]['address_name']
        x = json_obj['documents'][0]['x']
        y = json_obj['documents'][0]['y']
        post_num = json_obj['documents'][0]['road_address']['zone_no']
    except:
        join_place = search_place
        place = search_place
        address = None
        x = None
        y = None
        post_num = None

    value_list.append(join_place)
    value_list.append(place)
    value_list.append(address)
    value_list.append(x)
    value_list.append(y)
    value_list.append(post_num)
    row_list.append(value_list)

# 새로운 place_df생성
place_df = spark.createDataFrame(row_list, schema=col_list).dropDuplicates(['join_place'])

# 최종 결과물
df_final = df.join(place_df, df.place == place_df.join_place, 'left') \
    .drop(df.place).drop(place_df.join_place) \
    .orderBy(col('start_period').desc()) \
    .coalesce(1).withColumn('_c0', monotonically_increasing_id())

# 배포용 파일
#df_final.write.format('parquet').mode("overwrite").save("file:///home/ubuntu/yogi6/tr_data/crawling/vsn/init/vsn.parquet")
df_final.write.format('parquet').mode("overwrite").save("file:///home/ubuntu/yogi6/tr_data/crawling/init/vsn.parquet")

# 1차 가공된 파일
#df_final.write.format('parquet').mode("overwrite").save("hdfs:///user/ubuntu/yogi6/tr_data/crawling/vsn/init/vsn.parquet")
df_final.write.format('parquet').mode("overwrite").save("hdfs:///user/ubuntu/yogi6/tr_data/crawling/init/vsn.parquet")
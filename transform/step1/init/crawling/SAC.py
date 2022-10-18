from pyspark.sql.functions import col
from pyspark.sql.functions import when
from pyspark.sql.functions import to_date
from pyspark.sql.functions import substring
from pyspark.sql.functions import split
from pyspark.sql.functions import trim
from pyspark.sql.functions import lit
from pyspark.sql.functions import monotonically_increasing_id
import pandas as pd
import json
from pprint import pprint
import requests

##spark-submit 실행파일시
from pyspark.sql import SparkSession
spark =SparkSession.builder.getOrCreate()


# 하둡에서 파일 불러오기
df = spark.read.format("csv").option("header", "true").option("multiline", "true").option("quote", "\"").option(
    "escape", "\"").load("yogi6/raw_data/crawling/init/sac_all.csv")
'''
df = spark.read.format("csv").option("header", "true").option("multiline", "true").option("quote", "\"").option(
    "escape", "\"").load("yogi6/raw_data/crawling/sac/init/sac_all.csv")
'''
# 1차 가공
df = df.dropDuplicates(['exhibition_name']) \
    .withColumn('exhibition_period',
                when(col('exhibition_period').substr(1, 4) >= '2016', col('exhibition_period')).otherwise(None)) \
    .dropna('any', None, ['exhibition_name', 'exhibition_period']) \
    .filter(col('exhibition_period').contains('~')) \
    .withColumn('start_period',
                to_date(substring(trim(split('exhibition_period', '~').getItem(0)), 1, 10), 'yyyy-MM-dd')) \
    .withColumn('end_period', to_date(substring(trim(split('exhibition_period', '~').getItem(1)), 1, 10), 'yyyy-MM-dd')) \
    .drop(col('exhibition_period')).drop(col('_c0')) \
    .withColumn('place', lit('예술의전당')) \
    .orderBy(col('start_period').desc())

pd_df = df.toPandas()

##파일 저장##
# 분석, 리뷰크롤링용 csv파일
#pd_df.to_csv('~/yogi6/ds/file/sac.csv', encoding="utf-8-sig")

##df_final생성##
target_list = df.select(col('place')).collect()
place_list = list(set(map(lambda x: x[0], target_list)))

address_list = []

# 도로주소를 알기위한 api호출(키워드검색)
for search_place in place_list:
    url = f"https://dapi.kakao.com/v2/local/search/keyword.json?query={search_place}"
    kakao_key = "eeb4d25bd0990160503da341e8678475"
    result = requests.get(url, headers={"Authorization": f"KakaoAK {kakao_key}"})
    json_obj = result.json()
    try:
        address_list.append(json_obj['documents'][0]['road_address_name'])
    except:
        address_list.append(None)

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

place_df = spark.createDataFrame(row_list, schema=col_list)

# 최종 결과물
df_final = df.join(place_df, df.place == place_df.place, 'left') \
    .drop(place_df.place) \
    .orderBy(col('start_period').desc()) \
    .coalesce(1).withColumn('_c0', monotonically_increasing_id())

# 배포용 파일
#df_final.write.format('parquet').mode("overwrite").save("file:///home/ubuntu/yogi6/tr_data/crawling/sac/init/sac.parquet")
df_final.write.format('parquet').mode("overwrite").save("file:///home/ubuntu/yogi6/tr_data/crawling/init/sac.parquet")
# 1차 가공된 파일
#df_final.write.format('parquet').mode("overwrite").save("hdfs:///user/ubuntu/yogi6/tr_data/crawling/sac/init/sac.parquet")
df_final.write.format('parquet').mode("overwrite").save("hdfs:///user/ubuntu/yogi6/tr_data/crawling/init/sac.parquet")


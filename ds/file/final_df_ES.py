from pyspark.sql.functions import *
from pyspark.sql import SparkSession
spark =SparkSession.builder.getOrCreate()
# 하둡에서 파일 불러오기
df = spark.read.format("csv").option("header", "true").option("multiline", "true").option("quote", "\"").option(
    "escape", "\"").load("hdfs:///user/ubuntu/yogi6/ds/file/exhibition_final.csv")

pd_df = df.select(col('name'), col('poster_link'), col('start_period').cast('string'), col('end_period').cast('string'))\
      .withColumn('start_period', regexp_replace('start_period', '-',''))\
      .withColumn('end_period', regexp_replace('end_period', '-',''))\
      .toPandas()

pd_df.to_csv('~/yogi6/ds/file/exhibition_final_ES.csv', index=False, encoding="utf-8-sig")

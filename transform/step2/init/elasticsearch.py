from pyspark.sql.functions import *

#파이썬 파일 생성시
from pyspark.sql import SparkSession
spark =SparkSession.builder.getOrCreate()

user="root"
password="yogi220930"
url="jdbc:mysql://localhost:3306/yogi6"
driver="com.mysql.cj.jdbc.Driver"
dbtable="exhibition"

exhibition = spark.read.jdbc(url, dbtable, properties={"driver": driver, "user": user, "password": password}) \
    .select(col('exhibition_id'), col('name'), col('poster_link'), col('start_period'), col('end_period')) \
    .toPandas()

exhibition.to_csv(f'~/yogi6/model_data/exhibition_final_ES2.csv', encoding="utf-8-sig", index=False)

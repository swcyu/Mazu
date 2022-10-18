from pyspark.sql.functions import *
from pyspark.sql import Row

#파이썬 파일 생성시
from pyspark.sql import SparkSession
spark =SparkSession.builder.getOrCreate()

user="root"
password="yogi220930"
url="jdbc:mysql://localhost:3306/yogi5"
driver="com.mysql.cj.jdbc.Driver"
dbtable="exhibition"

recommend_df = spark.read.format("csv").option("header", "true") \
    .option("multiline", "true").option("quote", "\"").option("escape", "\"") \
    .load("file:///home/ubuntu/yogi6/model_data/recommend.csv")


cluster_df = spark.read.format("csv").option("header", "true") \
    .option("multiline", "true").option("quote", "\"").option("escape", "\"") \
    .load("file:///home/ubuntu/yogi6/model_data/cluster.csv")\
    .select(col('exhibition_id'), col('find_cluster_exhi').alias('cluster'))

final_df = recommend_df.join(cluster_df, recommend_df.exhibition_id == cluster_df.exhibition_id, 'left')\
    .dropna('all', None, 'cluster')\
    .drop(cluster_df.exhibition_id)\
    .withColumn('exhibition_id', col('exhibition_id').cast('string'))\
    .withColumn('start_period', to_date(col('start_period'), 'yyyy-MM-dd'))\
    .withColumn('end_period', to_date(col('end_period'), 'yyyy-MM-dd'))\
    .orderBy(col('start_period').desc())\
    .withColumn('exhibition_id', split(col('exhibition_id'), "[.]").getItem(0))\
    .withColumn('place_id', lpad(recommend_df.place_id, 5, '0'))

pd_df = final_df.toPandas()
pd_df.to_csv('~/yogi6/model_data/exhibition_mysql.csv', encoding="utf-8-sig", index=False)

final_df.write.mode('overwrite').option('truncate', 'true').jdbc(url, dbtable, properties={"driver": driver, "user": user, "password": password})


'''
#exhibition_id 생성
row_list = []
for i in range(final_df.count()):
    row = Row('id', 'exhibition_id')
    row_list.append(row(i, '2016010100' + str(i).zfill(4)))

rdd=spark.sparkContext.parallelize(row_list)
exhibition_id_df = spark.createDataFrame(rdd)

final_df = final_df.coalesce(1).withColumn('id', monotonically_increasing_id())

final_df = final_df.join(exhibition_id_df, final_df.id == exhibition_id_df.id, 'inner') \
    .drop(final_df.id).drop(exhibition_id_df.id) \
    .select(col('exhibition_id'), col('name'), col('poster_link'), col('description'), col('detail_place'), col('start_period'), col('end_period'), col('place_id'), col('recommend_exhi'), col('recommend_book'), col('recommend_movie'), col('cluster')) \
    .orderBy(col('exhibition_id'))

final_df.write.mode('overwrite').option('truncate', 'true').jdbc(url, dbtable, properties={"driver": driver, "user": user, "password": password})

'''

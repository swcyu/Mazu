from pyspark.sql.functions import *

from pyspark.sql import SparkSession
spark =SparkSession.builder.getOrCreate()

df = spark.read.option("multiline","true").json('hdfs:///user/ubuntu/yogi6/raw_data/api/movie/movie*.json')
df_temp = df.select(explode(col('movie')).alias('temp'))

movie = df_temp.select(col('temp.DOCID').alias('id'), col('temp.title')\
    .alias('name'), col('temp.directors.director.directorNm').alias('director'), col('temp.plots.plot.plotLang')[0].alias('plotLang'), col('temp.plots.plot.plotText')[0]\
    .alias('description'), col('temp.prodYear').alias('prodYear'))\
    .dropDuplicates(['id']).filter(col('plotLang') == '한국어')\
    .drop(col('plotLang')).drop(col('id'))
    #.coalesce(1).withColumn('movie_id', monotonically_increasing_id())

pd_df = movie.toPandas()
pd_df.to_csv('~/yogi6/ds/file/movie.csv', encoding="utf-8-sig", index=False)
'''
user="root"
password="yogi220930"
url="jdbc:mysql://localhost:3306/yogi5"
driver="com.mysql.cj.jdbc.Driver"
dbtable="movie"

movie.write.jdbc(url, dbtable, "append", properties={"driver": driver, "user": user, "password": password})
'''

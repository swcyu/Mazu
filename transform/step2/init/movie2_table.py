from pyspark.sql.functions import *
from pyspark.sql import SparkSession

spark =SparkSession.builder.getOrCreate()



# 영화 합치기
movie_csv = spark.read.option("header","true").option("multiline","true").option("quote", "\"").option("escape","\"").csv('yogi6/raw_data/api/movie2/movie_final*.csv')
# 포스터 링크 null값 행 제거, name 중복 값 제거
movie = movie_csv.dropna(subset=['poster_link']).select(col('name'), col('poster_link'), col('director'), col('description')).dropDuplicates(['name'])\
        .withColumn('name', trim(col('name')))

pd_df = movie.toPandas()
pd_df.to_csv('~/yogi6/ds/file/movie2.csv', encoding="utf-8-sig", index=False)


# movie2는 movie1에서 전처리 되어 나온 파일에 poster_link 컬럼 추가하여 DB에 넣는 과정입니다.
# DB 명시
user="root"
password="yogi220930"
url="jdbc:mysql://localhost:3306/yogi6"
driver="com.mysql.cj.jdbc.Driver"
dbtable="movie"

# to DB
movie.write.jdbc(url, dbtable, "append", properties={"driver": driver, "user": user, "password": password})

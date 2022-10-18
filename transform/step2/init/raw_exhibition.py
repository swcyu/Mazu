from pyspark.sql.functions import *

#파이썬 파일 생성시
from pyspark.sql import SparkSession
spark =SparkSession.builder.getOrCreate()

user="root"
password="yogi220930"
url="jdbc:mysql://localhost:3306/yogi6"
driver="com.mysql.cj.jdbc.Driver"

#place 테이블용 파일 불러오기
vsn_df = spark.read.format('parquet').load("hdfs:///user/ubuntu/yogi6/tr_data/crawling/init/vsn.parquet").drop(col('_c0'))
museum_df = spark.read.format('parquet').load("hdfs:///user/ubuntu/yogi6/tr_data/crawling/init/museum.parquet").drop(col('_c0'))
mcst_df = spark.read.format('parquet').load("hdfs:///user/ubuntu/yogi6/tr_data/crawling/init/mcst.parquet").drop(col('_c0')).drop(col('place_name'))
mmca_df = spark.read.format('parquet').load("hdfs:///user/ubuntu/yogi6/tr_data/crawling/init/mmca.parquet").drop(col('_c0')).drop(col('place_name'))
sac_df = spark.read.format('parquet').load("hdfs:///user/ubuntu/yogi6/tr_data/crawling/init/sac.parquet").drop(col('_c0'))
sema_df = spark.read.format('parquet').load("hdfs:///user/ubuntu/yogi6/tr_data/crawling/init/sema.parquet").drop(col('_c0'))
sjc_df = spark.read.format('parquet').load("hdfs:///user/ubuntu/yogi6/tr_data/crawling/init/sjc.parquet").drop(col('_c0'))
ddp_df = spark.read.format('parquet').load("hdfs:///user/ubuntu/yogi6/tr_data/crawling/init/ddp.parquet").drop(col('_c0'))
api_museum_df = spark.read.format('parquet').load("hdfs:///user/ubuntu/yogi6/tr_data/api/museum_all.parquet").drop(col('_c0'))


#파일 합치기
all_df = vsn_df.union(api_museum_df).union(museum_df).union(sjc_df).union(sac_df).union(sema_df).union(ddp_df).union(mmca_df).union(mcst_df)

##1. 덩어리 저장##
exhibition_final_df = all_df.withColumn('drop_name', regexp_replace('exhibition_name', r'[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\" 《》]', ''))\
    .coalesce(1).dropDuplicates(['drop_name'])\
    .drop(col('drop_name'))\
    .dropna('all', None, 'post_num')\
    .filter(col('post_num')!='')\
    .withColumn('exhibition_description', trim(col('exhibition_description')))\
    .withColumn('exhibition_description', regexp_replace(col('exhibition_description'), '&gt;', '>'))\
    .withColumn('exhibition_description', regexp_replace(col('exhibition_description'), '&lt;', '<'))\
    .withColumn('exhibition_name', regexp_replace(col('exhibition_name'), '&gt;', '>'))\
    .withColumn('exhibition_name', regexp_replace(col('exhibition_name'), '&lt;', '<'))\
    .withColumn('exhibition_description', regexp_replace(col('exhibition_description'), '맑은 ', ''))\
    .withColumn('exhibition_description', regexp_replace(col('exhibition_description'), '맑은', ''))\
    .withColumn('exhibition_description', regexp_replace(col('exhibition_description'), ' 맑은', ''))\
    .withColumn('exhibition_description', regexp_replace(col('exhibition_description'), '고딕 ', ''))\
    .withColumn('exhibition_description', regexp_replace(col('exhibition_description'), '고딕', ''))\
    .withColumn('exhibition_description', regexp_replace(col('exhibition_description'), '돋움', ''))\
    .withColumn('exhibition_description', regexp_replace(col('exhibition_description'), '맑은돋움', ''))

#dbtable="exhibition_all"
#exhibition_final_df.write.mode('overwrite').jdbc(url, dbtable, properties={"driver": driver, "user": user, "password": password})

##2. model로 들어갈 csv파일 만들기##
df_exhi = exhibition_final_df.select(col('exhibition_name').alias('name'), col('poster_link'), col('exhibition_description').alias('description'), col('exhibition_place').alias('detail_place'), col('start_period'), col('end_period'), col('post_num').alias('place_id'))\
    .toPandas()
#df_exhi.select(col('start_period'), col('end_period')).show(df_exhi.count())
df_exhi.to_csv('~/yogi6/model_data/exhibition_final.csv', encoding="utf-8-sig")


##3. place table에 저장##
place_df = all_df.select(col('post_num'), col('place').alias('name'), col('address'), col('x'), col('y'))\
    .dropna('all', None, 'post_num')\
    .coalesce(1).dropDuplicates(['post_num'])\
    .filter(col('post_num') != '')\
    .orderBy(col('post_num'))\
    .select(col('post_num').alias('place_id'), col('name'), col('address'), col('x'), col('y'))

dbtable="exhibition_place"
place_df.write.mode('overwrite').option('truncate', 'true').jdbc(url, dbtable, properties={"driver": driver, "user": user, "password": password})

from pyspark.sql.functions import *
from pyspark.sql import Row

from datetime import datetime

time = datetime.now()
now = time.strftime('%Y%m%d')
#파이썬 파일 생성시
from pyspark.sql import SparkSession
spark =SparkSession.builder.getOrCreate()

user="root"
password="yogi220930"
url="jdbc:mysql://localhost:3306/yogi6"
driver="com.mysql.cj.jdbc.Driver"

#place 테이블용 파일 불러오기
vsn_df = spark.read.format('parquet').load("hdfs:///user/ubuntu/yogi6/tr_data/crawling/init/vsn.parquet").drop(col('_c0'))\
    .select(col('exhibition_name'), col('poster_link'), col('exhibition_description'), col('exhibition_place'), col('start_period'), col('end_period'), col('post_num'))
museum_df = spark.read.format('parquet').load("hdfs:///user/ubuntu/yogi6/tr_data/crawling/init/museum.parquet").drop(col('_c0'))\
    .select(col('exhibition_name'), col('poster_link'), col('exhibition_description'), col('exhibition_place'), col('start_period'), col('end_period'), col('post_num'))
mcst_df = spark.read.format('parquet').load("hdfs:///user/ubuntu/yogi6/tr_data/crawling/init/mcst.parquet").drop(col('_c0')).drop(col('place_name'))\
    .select(col('exhibition_name'), col('poster_link'), col('exhibition_description'), col('exhibition_place'), col('start_period'), col('end_period'), col('post_num'))
mmca_df = spark.read.format('parquet').load("hdfs:///user/ubuntu/yogi6/tr_data/crawling/init/mmca.parquet").drop(col('_c0')).drop(col('place_name'))\
    .select(col('exhibition_name'), col('poster_link'), col('exhibition_description'), col('exhibition_place'), col('start_period'), col('end_period'), col('post_num'))
sac_df = spark.read.format('parquet').load("hdfs:///user/ubuntu/yogi6/tr_data/crawling/init/sac.parquet").drop(col('_c0'))\
    .select(col('exhibition_name'), col('poster_link'), col('exhibition_description'), col('exhibition_place'), col('start_period'), col('end_period'), col('post_num'))
sema_df = spark.read.format('parquet').load("hdfs:///user/ubuntu/yogi6/tr_data/crawling/init/sema.parquet").drop(col('_c0'))\
    .select(col('exhibition_name'), col('poster_link'), col('exhibition_description'), col('exhibition_place'), col('start_period'), col('end_period'), col('post_num'))
sjc_df = spark.read.format('parquet').load("hdfs:///user/ubuntu/yogi6/tr_data/crawling/init/sjc.parquet").drop(col('_c0'))\
    .select(col('exhibition_name'), col('poster_link'), col('exhibition_description'), col('exhibition_place'), col('start_period'), col('end_period'), col('post_num'))
ddp_df = spark.read.format('parquet').load("hdfs:///user/ubuntu/yogi6/tr_data/crawling/init/ddp.parquet").drop(col('_c0'))\
    .select(col('exhibition_name'), col('poster_link'), col('exhibition_description'), col('exhibition_place'), col('start_period'), col('end_period'), col('post_num'))
#api_museum_df = spark.read.format('parquet').load("hdfs:///user/ubuntu/yogi6/tr_data/api/museum_all.parquet").drop(col('_c0'))\


#파일 합치기
final_df = vsn_df.union(museum_df).union(sjc_df).union(sac_df).union(sema_df).union(ddp_df).union(mmca_df).union(mcst_df)\
    .withColumn('drop_name', regexp_replace('exhibition_name', r'[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\" 《》]', ''))\
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

#all_df.select(col('start_period'), col('end_period')).show(all_df.count())

#print(all_df.printSchema())

row_list = []
for i in range(final_df.count()):
    row = Row('id', 'exhibition_id')
    row_list.append(row(i, '2016010100' + str(i).zfill(4)))

rdd=spark.sparkContext.parallelize(row_list)
exhibition_id_df = spark.createDataFrame(rdd)

final_df = final_df.orderBy(col('start_period').desc()) \
    .coalesce(1).withColumn('id', monotonically_increasing_id())

past_final_df = final_df.join(exhibition_id_df, final_df.id == exhibition_id_df.id, 'inner') \
    .drop(final_df.id).drop(exhibition_id_df.id)\
    .select(col('exhibition_id'), col('exhibition_name'), col('poster_link'), col('exhibition_description'), col('exhibition_place'), col('start_period'), col('end_period'), col('post_num'))

#count = final_df.count()
#final_df.select(col('exhibition_id'), col('start_period'), col('end_period')).show(count)

#print(final_df.printSchema(), count)


vsn_df = spark.read.format('parquet').load(f"hdfs:///user/ubuntu/yogi6/tr_data/crawling/{now}/vsn.parquet")
museum_df = spark.read.format('parquet').load(f"hdfs:///user/ubuntu/yogi6/tr_data/crawling/{now}/museum.parquet")
mcst_df = spark.read.format('parquet').load(f"hdfs:///user/ubuntu/yogi6/tr_data/crawling/{now}/mcst.parquet")
mmca_df = spark.read.format('parquet').load(f"hdfs:///user/ubuntu/yogi6/tr_data/crawling/{now}/mmca.parquet")
sema_df = spark.read.format('parquet').load(f"hdfs:///user/ubuntu/yogi6/tr_data/crawling/{now}/sema.parquet")
sjc_df = spark.read.format('parquet').load(f"hdfs:///user/ubuntu/yogi6/tr_data/crawling/{now}/sjc.parquet")
ddp_df = spark.read.format('parquet').load(f"hdfs:///user/ubuntu/yogi6/tr_data/crawling/{now}/ddp.parquet")

pre_final_df = vsn_df.union(museum_df).union(sjc_df).union(sema_df).union(ddp_df).union(mmca_df).union(mcst_df)\
    .select(col('exhibition_id'), col('exhibition_name'), col('poster_link'), col('exhibition_description'), col('exhibition_place'), col('start_period'), col('end_period'), col('post_num'))

final_df = pre_final_df.union(past_final_df)\
    .withColumn('drop_name', regexp_replace('exhibition_name', r'[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\" 《》]', ''))\
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

df_exhi = final_df.select(col('exhibition_id'), col('exhibition_name').alias('name'), col('poster_link'), col('exhibition_description').alias('description'), col('exhibition_place').alias('detail_place'), col('start_period'), col('end_period'), col('post_num').alias('place_id'))\
    .toPandas()

df_exhi.to_csv(f'~/yogi6/model_data/exhibition_final_ES2.csv', encoding="utf-8-sig", index=False)

'''
#place 테이블용 파일 불러오기
vsn_df = spark.read.format('parquet').load("hdfs:///user/ubuntu/yogi6/tr_data/crawling/init/vsn.parquet").drop(col('_c0'))\
    .select(col('post_num'), col('place'), col('address'), col('x'), col('y'))
museum_df = spark.read.format('parquet').load("hdfs:///user/ubuntu/yogi6/tr_data/crawling/init/museum.parquet").drop(col('_c0'))\
    .select(col('post_num'), col('place'), col('address'), col('x'), col('y'))
mcst_df = spark.read.format('parquet').load("hdfs:///user/ubuntu/yogi6/tr_data/crawling/init/mcst.parquet").drop(col('_c0')).drop(col('place_name'))\
    .select(col('post_num'), col('place'), col('address'), col('x'), col('y'))
mmca_df = spark.read.format('parquet').load("hdfs:///user/ubuntu/yogi6/tr_data/crawling/init/mmca.parquet").drop(col('_c0')).drop(col('place_name'))\
    .select(col('post_num'), col('place'), col('address'), col('x'), col('y'))
sac_df = spark.read.format('parquet').load("hdfs:///user/ubuntu/yogi6/tr_data/crawling/init/sac.parquet").drop(col('_c0'))\
    .select(col('post_num'), col('place'), col('address'), col('x'), col('y'))
sema_df = spark.read.format('parquet').load("hdfs:///user/ubuntu/yogi6/tr_data/crawling/init/sema.parquet").drop(col('_c0'))\
    .select(col('post_num'), col('place'), col('address'), col('x'), col('y'))
sjc_df = spark.read.format('parquet').load("hdfs:///user/ubuntu/yogi6/tr_data/crawling/init/sjc.parquet").drop(col('_c0'))\
    .select(col('post_num'), col('place'), col('address'), col('x'), col('y'))
ddp_df = spark.read.format('parquet').load("hdfs:///user/ubuntu/yogi6/tr_data/crawling/init/ddp.parquet").drop(col('_c0'))\
    .select(col('post_num'), col('place'), col('address'), col('x'), col('y'))

past_final_df = vsn_df.union(museum_df).union(sjc_df).union(sac_df).union(sema_df).union(ddp_df).union(mmca_df).union(mcst_df)


vsn_df = spark.read.format('parquet').load(f"hdfs:///user/ubuntu/yogi6/tr_data/crawling/{now}/vsn.parquet")\
    .select(col('post_num'), col('place'), col('address'), col('x'), col('y'))
museum_df = spark.read.format('parquet').load(f"hdfs:///user/ubuntu/yogi6/tr_data/crawling/{now}/museum.parquet")\
    .select(col('post_num'), col('place'), col('address'), col('x'), col('y'))
mcst_df = spark.read.format('parquet').load(f"hdfs:///user/ubuntu/yogi6/tr_data/crawling/{now}/mcst.parquet")\
    .select(col('post_num'), col('place'), col('address'), col('x'), col('y'))
mmca_df = spark.read.format('parquet').load(f"hdfs:///user/ubuntu/yogi6/tr_data/crawling/{now}/mmca.parquet")\
    .select(col('post_num'), col('place'), col('address'), col('x'), col('y'))
sema_df = spark.read.format('parquet').load(f"hdfs:///user/ubuntu/yogi6/tr_data/crawling/{now}/sema.parquet")\
    .select(col('post_num'), col('place'), col('address'), col('x'), col('y'))
sjc_df = spark.read.format('parquet').load(f"hdfs:///user/ubuntu/yogi6/tr_data/crawling/{now}/sjc.parquet")\
    .select(col('post_num'), col('place'), col('address'), col('x'), col('y'))
ddp_df = spark.read.format('parquet').load(f"hdfs:///user/ubuntu/yogi6/tr_data/crawling/{now}/ddp.parquet")\
    .select(col('post_num'), col('place'), col('address'), col('x'), col('y'))

pre_final_df = vsn_df.union(museum_df).union(sjc_df).union(sema_df).union(ddp_df).union(mmca_df).union(mcst_df)

place_df = pre_final_df.union(past_final_df)\
    .dropna('all', None, 'post_num')\
    .coalesce(1).dropDuplicates(['post_num'])\
    .filter(col('post_num') != '')\
    .orderBy(col('post_num'))\
    .select(col('post_num').alias('place_id'), col('place').alias('name'), col('address'), col('x'), col('y'))

#place_df.show(place_df.count())
#print(place_df.printSchema())

dbtable="exhibition_place"
place_df.write.mode('overwrite').option('truncate', 'true').jdbc(url, dbtable, properties={"driver": driver, "user": user, "password": password})
'''
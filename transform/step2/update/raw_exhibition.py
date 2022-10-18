from pyspark.sql.functions import *

from datetime import datetime

time = datetime.now()
now = time.strftime('%Y%m%d')

#파이썬 파일 생성시
from pyspark.sql import SparkSession
spark =SparkSession.builder.getOrCreate()

user="root"
password="yogi220930"
driver="com.mysql.cj.jdbc.Driver"

##과거 전시정보 불러오기##
url="jdbc:mysql://localhost:3306/yogi5"
dbtable="exhibition"
past_exhibition = spark.read.jdbc(url, dbtable, properties={"driver": driver, "user": user, "password": password})\
    .select(col('exhibition_id'), col('name').alias('exhibition_name'), col('poster_link'), col('detail_place'), col('description'), col('start_period'), col('end_period'), col('place_id'))

dbtable="exhibition_place"
past_exhibition_place = spark.read.jdbc(url, dbtable, properties={"driver": driver, "user": user, "password": password})
past_exhibition_final = past_exhibition.join(past_exhibition_place, past_exhibition.place_id == past_exhibition_place.place_id, 'left')\
    .drop(past_exhibition_place.place_id)\
    .select(col('exhibition_id'), col('exhibition_name'),col('poster_link'),col('description').alias('exhibition_description'),col('detail_place').alias('exhibition_place'),col('start_period'),col('end_period'),col('name').alias('place'),col('address'),col('x'),col('y'),col('place_id').alias('post_num'))

##최신 전시 불러오기##
vsn_df = spark.read.format('parquet').load(f"hdfs:///user/ubuntu/yogi6/tr_data/crawling/{now}/vsn.parquet")
museum_df = spark.read.format('parquet').load(f"hdfs:///user/ubuntu/yogi6/tr_data/crawling/{now}/museum.parquet")
mcst_df = spark.read.format('parquet').load(f"hdfs:///user/ubuntu/yogi6/tr_data/crawling/{now}/mcst.parquet")
mmca_df = spark.read.format('parquet').load(f"hdfs:///user/ubuntu/yogi6/tr_data/crawling/{now}/mmca.parquet")
sema_df = spark.read.format('parquet').load(f"hdfs:///user/ubuntu/yogi6/tr_data/crawling/{now}/sema.parquet")
sjc_df = spark.read.format('parquet').load(f"hdfs:///user/ubuntu/yogi6/tr_data/crawling/{now}/sjc.parquet")
ddp_df = spark.read.format('parquet').load(f"hdfs:///user/ubuntu/yogi6/tr_data/crawling/{now}/ddp.parquet")

all_df = vsn_df.union(museum_df).union(sjc_df).union(sema_df).union(ddp_df).union(mmca_df).union(mcst_df)

all_df.show(2)
all_df.printSchema()

pre_exhibition_final = all_df.withColumn('drop_name', regexp_replace('exhibition_name', r'[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\" 《》]', ''))\
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

pre_exhibition_final.select(col('start_period'), col('end_period')).show(pre_exhibition_final.count())


#과거와 현재 합친 전시 데이터
exhibition_final_df = pre_exhibition_final.union(past_exhibition_final)\
    .orderBy(col('exhibition_id').asc()).coalesce(1).dropDuplicates(['exhibition_name'])


##model로 들어갈 csv파일 만들기##
df_exhi = exhibition_final_df.select(col('exhibition_id'), col('exhibition_name').alias('name'), col('poster_link'), col('exhibition_description').alias('description'), col('exhibition_place').alias('detail_place'), col('start_period'), col('end_period'), col('post_num').alias('place_id'))\
    .toPandas()

df_exhi.to_csv(f'~/yogi6/model_data/exhibition_final.csv', encoding="utf-8-sig", index=False)

##place table에 저장##
place_df = exhibition_final_df.select(col('post_num'), col('place').alias('name'), col('address'), col('x'), col('y'))\
    .dropna('all', None, 'post_num')\
    .coalesce(1).dropDuplicates(['post_num'])\
    .filter(col('post_num') != '')\
    .orderBy(col('post_num'))\
    .select(col('post_num').alias('place_id'), col('name'), col('address'), col('x'), col('y'))

url="jdbc:mysql://localhost:3306/yogi5"
dbtable="exhibition_place"

place_df.write.mode('overwrite').jdbc(url, dbtable, properties={"driver": driver, "user": user, "password": password})

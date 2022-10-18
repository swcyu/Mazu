from pyspark.sql.functions import *


#파이썬 파일 생성시
from pyspark.sql import SparkSession
spark =SparkSession.builder.getOrCreate()

user="root"
password="yogi220930"
url="jdbc:mysql://localhost:3306/yogi6"
driver="com.mysql.cj.jdbc.Driver"
dbtable="book"

book1 = spark.read.format("csv").option("header","true").option("multiline","true").option("quote", "\"").option("escape","\"").load("yogi6/raw_data/api/book/book.csv")\
    .select(col('title').alias('name'), col('author').alias('writer'), col('description'))

book2 = spark.read.option("header","true").option("multiline","true").option("quote", "\"").option("escape","\"").csv('hdfs:///user/ubuntu/yogi6/raw_data/api/book/book_*.csv')\
    .withColumn('drop_title', regexp_replace('title', r'[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\" 《》]', ''))\
    .dropDuplicates(['drop_title'])\
    .drop(col('drop_title'))\
    .dropna(how='any', subset=['title', 'description'])\
    .filter(col('title') != ' ')\
    .withColumn('rights', trim(split(col('rights'), '/').getItem(0)))\
    .withColumn('rights', trim(regexp_replace('rights', '[.,]', '')))\
    .withColumn('rights', trim(split(col('rights'), ';').getItem(0)))\
    .withColumn('rights', when(col('rights').contains('&#'), None).when(col('rights') == '', None).otherwise(col('rights')))\
    .select(col('title').alias('name'), col('rights').alias('writer'), col('description'))

book = book1.union(book2)\
    .withColumn('drop_title', regexp_replace('name', r'[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\" 《》]', ''))\
    .coalesce(1).dropDuplicates(['drop_title'])\
    .drop(col('drop_title'))\
    .withColumn('description', regexp_replace('description', '&lt;', '<'))\
    .withColumn('description', regexp_replace('description', '&gt;', '>'))


# book.count() :41162

pd_df = book.toPandas()
pd_df.to_csv('~/yogi6/model_data/book.csv', encoding="utf-8-sig")

# book.write.mode('overwrite').option('truncate', 'true').jdbc(url, dbtable, properties={"driver": driver, "user": user, "password": password})

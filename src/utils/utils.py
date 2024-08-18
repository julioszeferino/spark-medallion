import os

from pyspark.sql import SparkSession
from pyspark import SparkConf


def init_spark(func):

    def wrapper(*args, **kwargs):
        jar_path = "venv/lib/python3.10/site-packages/pyspark/jars"
        jars = ",".join([os.path.join(jar_path, jar)
                        for jar in os.listdir(jar_path) if jar.endswith(".jar")])

        spark = SparkSession.builder \
            .appName("Change Data Feed") \
            .master("local[*]") \
            .config("spark.jars", jars) \
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
            .getOrCreate()

        spark.sparkContext.setLogLevel("INFO")

        resultado = func(spark)

        return resultado
    return wrapper


@init_spark
def consumer(spark):

    df = spark.read.format("delta") \
        .load("./data/user/warehouse/gold/corridas")

    df \
        .write \
        .format("csv") \
        .mode("overwrite") \
        .option("header", "true") \
        .option("sep", ";") \
        .save("./data/user/consumer/corridas")

from utils.utils import init_spark


@init_spark
def cria_bronze(spark):

    path_fhvhv = "./data/user/landing_zone/fhvhv/2022/*.parquet"
    df_fhvhv = spark.read.parquet(path_fhvhv)

    path_zones = "./data/user/landing_zone/zones/zones.csv"
    df_zones = spark.read.option("delimiter", ",")\
        .option("header", True).csv(path_zones)

    df_fhvhv \
        .write \
        .format("delta") \
        .mode("overwrite") \
        .save("./data/user/warehouse/bronze/fhvhv")

    df_zones \
        .write \
        .format("delta") \
        .mode("overwrite") \
        .save("./data/user/warehouse/bronze/zones")

from pyspark.sql.functions import when, col, unix_timestamp, to_date
from utils.utils import init_spark


@init_spark
def cria_silver_fhvhv(spark):

    df = spark.read.format("delta") \
        .load("./data/user/warehouse/bronze/fhvhv") \
        .limit(100000)

    df.printSchema()

    df = substitui_numero_licensa(df)

    df_calcula_tempo_viagem = calcula_tempo(
        df,
        data_inicio="pickup_datetime",
        data_fim="dropoff_datetime",
        nome_coluna_duracao="duracao_viagem_minutos"
    )

    df_calcula_tempo_espera = calcula_tempo(
        df_calcula_tempo_viagem,
        data_inicio="request_datetime",
        data_fim="on_scene_datetime",
        nome_coluna_duracao="duracao_espera_minutos"
    )

    df = converte_milhas_km(df_calcula_tempo_espera)

    df = (
        df
        .withColumn("data_corrida", to_date(col("pickup_datetime")))
        .select("data_corrida", "PULocationID",
                "hvfhs_license_num", "duracao_viagem_minutos",
                "duracao_espera_minutos", "distancia_km",
                "base_passenger_fare", "tolls", "bcf", "sales_tax",
                "congestion_surcharge", "airport_fee", "tips", "driver_pay",
                "shared_match_flag", "wav_request_flag", "wav_match_flag"
                )
    )

    df \
        .write \
        .format("delta") \
        .mode("overwrite") \
        .save("./data/user/warehouse/silver/fhvhv_calculado")


def substitui_numero_licensa(df):

    columns = ["hvfhs_license_num_renamed", "pickup_datetime",
               "dropoff_datetime", "PULocationID",
               "request_datetime", "on_scene_datetime", "trip_miles",
               "base_passenger_fare", "tolls", "bcf", "sales_tax",
               "congestion_surcharge", "airport_fee", "tips", "driver_pay",
               "shared_match_flag", "wav_request_flag", "wav_match_flag"
               ]

    df_transformado = (
        df
        .withColumn(
            "hvfhs_license_num_renamed",
            when(col("hvfhs_license_num") == "HV0002", "Juno")
            .when(col("hvfhs_license_num") == "HV0003", "Uber")
            .when(col("hvfhs_license_num") == "HV0004", "Via")
            .when(col("hvfhs_license_num") == "HV0005", "Lyft")
            .otherwise("other")
        )
        .filter(col("hvfhs_license_num_renamed") != "other")
        .select(columns)
        .withColumnRenamed("hvfhs_license_num_renamed", "hvfhs_license_num")
    )

    return df_transformado


def calcula_tempo(df, data_inicio, data_fim, nome_coluna_duracao):

    df_transformado = (
        df
        .withColumn("tempo_inicial", unix_timestamp(col(data_inicio)))
        .withColumn("tempo_final", unix_timestamp(col(data_fim)))
        .withColumn(nome_coluna_duracao, ((col("tempo_final") - col("tempo_inicial")) / 60).cast("int"))
        .drop("tempo_inicial", "tempo_final")
    )

    return df_transformado


def converte_milhas_km(df):

    df_transformado = (
        df
        .withColumn("distancia_km", col("trip_miles") * 1.60934)
    )

    return df_transformado


@init_spark
def cria_silver_corridas(spark):

    df_zones = spark.read.format("delta") \
        .load("./data/user/warehouse/bronze/zones")
    df_zones.createOrReplaceTempView("zones")

    df_fhvhv_calculado = spark.read.format("delta") \
        .load("./data/user/warehouse/silver/fhvhv_calculado")
    df_fhvhv_calculado.createOrReplaceTempView("fhvhv_calculado")

    df = spark.sql("""
        SELECT
            fhvhv.data_corrida,
            zones.Zone as zona,
            fhvhv.hvfhs_license_num,
            fhvhv.duracao_viagem_minutos,
            fhvhv.duracao_espera_minutos,
            fhvhv.distancia_km,
            fhvhv.base_passenger_fare,
            fhvhv.tolls,
            fhvhv.bcf,
            fhvhv.sales_tax,
            fhvhv.congestion_surcharge,
            fhvhv.airport_fee,
            fhvhv.tips,
            fhvhv.driver_pay,
            CASE
                WHEN fhvhv.shared_match_flag = 'Y' THEN 1
                ELSE 0
            END as shared_match_flag,  
            CASE
                WHEN fhvhv.wav_request_flag = 'Y' THEN 1
                ELSE 0
            END as wav_request_flag,      
            CASE
                WHEN fhvhv.wav_match_flag = 'Y' THEN 1
                ELSE 0
            END as wav_match_flag      
        FROM fhvhv_calculado as fhvhv
        INNER JOIN zones
        ON CAST(fhvhv.PULocationID AS INT) = zones.LocationID
    """)

    df \
        .write \
        .format("delta") \
        .mode("overwrite") \
        .save("./data/user/warehouse/silver/corridas")

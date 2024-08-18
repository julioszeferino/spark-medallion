from utils.utils import init_spark


@init_spark
def cria_gold(spark):

    df = spark.read.format("delta") \
        .load("./data/user/warehouse/silver/corridas")
    df.createOrReplaceTempView("corridas")

    df = spark.sql("""
        SELECT
            data_corrida,
            zona as zona_inicio,
            hvfhs_license_num as licensa,
            AVG(duracao_viagem_minutos) as tempo_medio_viagem,
            AVG(duracao_espera_minutos) as tempo_medio_espera,
            AVG(distancia_km) as distancia_media,
            COUNT(*) as quantidade_corridas,
            ROUND((SUM(driver_pay) + SUM(tips)) * 5, 2) as valor_total_recebido,
            ROUND(((SUM(driver_pay) + SUM(tips)) - (SUM(tolls) + SUM(bcf) + SUM(sales_tax) + SUM(congestion_surcharge) + SUM(airport_fee))) * 5, 2) as valor_liquido_recebido,
            SUM(shared_match_flag) as qtde_viagens_compartilhadas,
            SUM(wav_match_flag) / SUM(wav_request_flag) as percentual_acessibilidade
        FROM corridas
        GROUP BY data_corrida, zona, hvfhs_license_num
    """)

    df.show(10)

    df \
        .write \
        .format("delta") \
        .mode("overwrite") \
        .save("./data/user/warehouse/gold/corridas")

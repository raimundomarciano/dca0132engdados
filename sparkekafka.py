from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import pyspark.sql.functions as F

# Criar sessão Spark
spark = SparkSession.builder \
    .appName("MongoDBDebeziumIntegration") \
    .master("local[*]") \
    .getOrCreate()

# Ler mensagens do Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "mongo.newdatabase.newcollection") \
    .load()

# Converter mensagens de binário para string
messages = df.selectExpr("CAST(value AS STRING)")

# Supondo que as mensagens estejam no formato JSON, você pode fazer a conversão para DataFrame
messages_json = messages.select(F.from_json(messages['value'], "loan DOUBLE").alias("data")).select("data.*")

# Adicionar coluna 'default' com base na variável 'loan'
messages_json_with_default = messages_json.withColumn(
    "default", 
    F.when(messages_json["loan"] > 100, "não vai pagar").otherwise("vai pagar")
)

# Função para processar e gravar em PostgreSQL
def process_batch(batch_df, batch_id):
    # Definindo as propriedades de conexão
    postgres_url = "jdbc:postgresql://postgres:5432/default_db"
    properties = {
        "user": "user",
        "password": "password",
        "driver": "org.postgresql.Driver"
    }

    # Gravar no PostgreSQL
    batch_df.write.jdbc(url=postgres_url, table="loan_info", mode="append", properties=properties)

# Escrever no PostgreSQL com foreachBatch
query = messages_json_with_default.writeStream \
    .outputMode("append") \
    .foreachBatch(process_batch) \
    .start()

query.awaitTermination()



# from pyspark.sql import SparkSession
# from pyspark.sql.functions import col

# # Criar sessão Spark
# spark = SparkSession.builder \
#     .appName("MongoDBDebeziumIntegration") \
#     .master("local[*]") \
#     .getOrCreate()

# # Ler mensagens do Kafka
# df = spark.readStream \
#     .format("kafka") \
#     .option("kafka.bootstrap.servers", "kafka:9092") \
#     .option("subscribe", "mongo.newdatabase.newcollection") \
#     .load()

# # Converter mensagens de binário para string
# messages = df.selectExpr("CAST(value AS STRING)")

# # Escrever no console
# # query = messages.writeStream \
# #     .outputMode("append") \
# #     .format("console") \
# #     .start()

# # Supondo que as mensagens estejam no formato JSON, você pode fazer a conversão para DataFrame
# # Aqui é necessário usar um método para desserializar as mensagens JSON, por exemplo:
# import pyspark.sql.functions as F
# messages_json = messages.select(F.from_json(messages['value'], "loan DOUBLE").alias("data")).select("data.*")

# # Aplicar transformação para verificar se loan é maior que 100
# messages_json_with_default = messages_json.withColumn(
#     "default", 
#     F.when(messages_json["loan"] > 100, "não vai pagar").otherwise("vai pagar")
# )

# # Função para processar cada micro-batch
# def process_batch(batch_df, batch_id):
#     # Aqui você pode usar o método .show() ou outras ações para processar os dados
#     batch_df.show()

# # Escrever no console com a função foreachBatch
# query = messages_json_with_default.writeStream \
#     .outputMode("append") \
#     .foreachBatch(process_batch) \
#     .start()

# query.awaitTermination()

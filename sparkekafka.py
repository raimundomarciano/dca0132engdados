from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import pyspark.sql.functions as F

from pyspark.sql.types import StructField, StructType, StringType, MapType, FloatType
 
schema = StructType([
    StructField("a", StringType(), True),
    StructField("loan", FloatType(), True)
])

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
messages_json = messages.select(F.from_json(messages['value'], schema).alias("data")).select("data.*")

messages_json_with_default = messages_json.withColumn(
    "default", 
    F.when(messages_json.loan > 100, "não vai pagar").otherwise("vai pagar")
)

# Função para processar e gravar em PostgreSQL
def process_batch(batch_df, batch_id):
     # Certificar-se de que o DataFrame tem ambas as colunas
    print("Batch DataFrame:")
    batch_df.show()

    # Definindo as propriedades de conexão
    postgres_url = "jdbc:postgresql://postgres:5432/default_db"
    properties = {
        "user": "user",
        "password": "password",
        "driver": "org.postgresql.Driver"
    }

    # Gravar no PostgreSQL
    batch_df.select("loan", "default").write.jdbc(url=postgres_url, table="loan_info", mode="append", properties=properties)

# Escrever no PostgreSQL com foreachBatch
query = messages_json_with_default.writeStream \
    .outputMode("append") \
    .foreachBatch(process_batch) \
    .start()

query.awaitTermination()
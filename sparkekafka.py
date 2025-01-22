from pyspark.sql import SparkSession

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

# Escrever no console
query = messages.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

query.awaitTermination()

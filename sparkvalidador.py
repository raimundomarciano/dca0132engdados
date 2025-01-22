from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr
from pymongo import MongoClient

# Criar sessão Spark
spark = SparkSession.builder \
    .appName("MongoDBDebeziumIntegration") \
    .master("local[*]") \
    .getOrCreate()

# Configurar conexão com MongoDB
mongo_client = MongoClient("mongodb://mongodb:27017")
mongo_db = mongo_client["newdatabase"]
mongo_collection = mongo_db["newcollection"]

# Função de validação
def validate_json(json_data):
    # Exemplo: validar se "age" existe e é maior que 0
    json_data["is_valid"] = (
        "age" in json_data and isinstance(json_data["age"], int) and json_data["age"] > 0
    )
    return json_data

# Ler mensagens do Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "mongo.newdatabase.newcollection") \
    .load()

# Converter mensagens de binário para string e JSON
messages = df.selectExpr("CAST(value AS STRING) as json_data")

# Transformação: Validar mensagens
validated_df = messages.rdd.map(lambda row: validate_json(eval(row.json_data))).toDF()

# Escrever mensagens validadas no MongoDB
def write_to_mongo(partition):
    for record in partition:
        mongo_collection.insert_one(record)

validated_df.writeStream \
    .foreachPartition(write_to_mongo) \
    .start() \
    .awaitTermination()

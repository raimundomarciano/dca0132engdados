from pyspark.sql import SparkSession
import pickle
import pandas as pd

# Cria uma sessão Spark
spark = SparkSession.builder.appName("SVMInference").getOrCreate()

# Lê os dados do Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "mongo.newdatabase.newcollection") \
    .load()

print("@@", df)

# Define o esquema (ajuste de acordo com seus dados)
df = df.selectExpr("CAST(value AS STRING)") 

print("XX", df)

# Pré-processamento (exemplo básico)
dado_pre_processado = df.na.fill(0)  # Preenche valores ausentes com 0

# Carrega o modelo
with open('/opt/bitnami/spark/work/svm_credit.pkl', 'rb') as f:
    modelo_svm = pickle.load(f)
    f.close()

with open('/opt/bitnami/spark/work/scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)
    f.close()

#data = dado_pre_processado.toPandas()
#data = data.values
#dado_normalizado = scaler.transform(data)
#previsoes = modelo_svm.predict(dado_normalizado)

# Escreve as predições em um sink (ex: console, banco de dados)
query = df.writeStream \
    .start()


query.awaitTermination()
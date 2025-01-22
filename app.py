# o objetivo desse programa é gerar uma API flask que permita a visualização dos dados
# no localhost:5050/data
from flask import Flask, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Configurar conexão com MongoDB
mongo_client = MongoClient("mongodb://mongodb:27017")
mongo_db = mongo_client["newdatabase"]
mongo_collection = mongo_db["newcollection"]

@app.route('/data', methods=['GET'])
def get_data():
    # Buscar os dados validados no MongoDB
    data = list(mongo_collection.find({}, {"_id": 0}))  # Ignorar o campo "_id" no retorno
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

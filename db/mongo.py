from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "e_trading")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def get_collection(name="cryptos"):
    return db[name]

def insert_crypto_data(data):
    collection = get_collection()
    if data:
        collection.insert_many(data)
        print(f"{len(data)} criptomonedas insertadas en MongoDB.")
    else:
        print("No hay datos para insertar.")

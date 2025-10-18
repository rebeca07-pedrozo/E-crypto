from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
uri = os.getenv("MONGO_URI")
print("Probando conexión con:", uri)

try:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    print("Conexión exitosa")
except Exception as e:
    print("Error:", e)



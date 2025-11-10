from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Cargar variables de entorno (.env)
load_dotenv()

# Leer las variables necesarias
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "e_trading")

# Crear conexión a MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]


def get_collection(name: str = "cryptos"):
    """Retorna una colección de la base de datos."""
    return db[name]


def insert_crypto_data(data: list):
    """Inserta múltiples documentos en la colección de criptomonedas."""
    collection = get_collection()
    if not data:
        print("⚠️ No hay datos para insertar.")
        return

    try:
        collection.insert_many(data)
        print(f"✅ {len(data)} criptomonedas insertadas en MongoDB.")
    except Exception as e:
        print(f"❌ Error al insertar datos: {e}")


# Este código está bajo licencia MIT.
# (c) 2025 Rebeca Pedrozo Cueto

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson.json_util import dumps
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URI = "mongodb+srv://rebecapc:22740876R@cluster0.v9ltmph.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["e_trading"]
collection = db["cryptos"]

@app.get("/")
def root():
    return {"message": "API de criptomonedas activa"}

@app.get("/cryptos")
def get_cryptos():
    cryptos = list(collection.find().sort("scraped_at", -1).limit(10))
    return json.loads(dumps(cryptos))

# analysis/queries.py
from db.mongo import get_collection
from bson.son import SON

def listar_criptos():
    coleccion = get_collection("cryptos")
    return list(coleccion.find({}))

def resumen_precios():
    coleccion = get_collection("cryptos")
    pipeline = [
        {
            "$group": {
                "_id": None,
                "max_price": {"$max": "$price_num"},
                "min_price": {"$min": "$price_num"},
                "avg_price": {"$avg": "$price_num"}
            }
        }
    ]
    resultado = list(coleccion.aggregate(pipeline))
    return resultado[0] if resultado else None

def buscar_por_nombre(nombre):
    coleccion = get_collection("cryptos")
    return coleccion.find_one({"name": nombre})

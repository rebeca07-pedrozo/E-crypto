import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from db.mongo import insert_crypto_data

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from datetime import datetime, timezone
from db.mongo import insert_crypto_data

def get_crypto_data_coingecko_api(limit=100):
    url = f"https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": limit,
        "page": 1,
        "sparkline": False
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        data = []
        for coin in result:
            data.append({
                "name": coin["name"],
                "symbol": coin["symbol"].upper(),
                "price": f"${coin['current_price']:,}",
                "price_num": coin["current_price"],
                "scraped_at": datetime.now(timezone.utc)
            })
        return data
    except Exception as e:
        print("Error al obtener datos desde la API de CoinGecko:", e)
        return []

if __name__ == "__main__":
    cryptos = get_crypto_data_coingecko_api(limit=100)
    if cryptos:
        insert_crypto_data(cryptos)
        print(f"{len(cryptos)} criptomonedas insertadas correctamente desde la API de CoinGecko.")
    else:
        print("No se encontraron criptomonedas para insertar.")

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from db.mongo import insert_crypto_data

def get_crypto_data(limit=10):
    url = "https://coinmarketcap.com/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    data = []
    rows = soup.select("tbody tr")[:limit]

    for row in rows:
        try:
            name = row.select_one("p.coin-item-name").text.strip()
            symbol = row.select_one("p.coin-item-symbol").text.strip()

            price_td = row.select("td")[3]
            price_text = price_td.find("span").text.strip()  # Ejemplo: "$26,000.50"

            price_num = float(price_text.replace("$", "").replace(",", ""))

            data.append({
                "name": name,
                "symbol": symbol,
                "price": price_text,
                "price_num": price_num,
                "scraped_at": datetime.now(timezone.utc)
            })

        except Exception as e:
            print("Error al procesar una fila:", e)
            continue

    return data

if __name__ == "__main__":
    crypto_list = get_crypto_data()
    for crypto in crypto_list:
        print(crypto)
    insert_crypto_data(crypto_list)

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from db.mongo import insert_crypto_data

def scrape_coinmarketcap_pages(num_pages=5):
    base_url = "https://coinmarketcap.com/"
    headers = {"User-Agent": "Mozilla/5.0"}
    all_data = []

    for page in range(1, num_pages + 1):
        print(f"Scraping página {page}...")
        url = base_url if page == 1 else f"{base_url}?page={page}"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        rows = soup.select("tbody tr")
        for row in rows:
            try:
                name = row.select_one("p.coin-item-name").text.strip()
                symbol = row.select_one("p.coin-item-symbol").text.strip()

                price_td = row.select("td")[3]
                price_text = price_td.find("span").text.strip()  
                price_num = float(price_text.replace("$", "").replace(",", ""))

                all_data.append({
                    "name": name,
                    "symbol": symbol,
                    "price": price_text,
                    "price_num": price_num,
                    "scraped_at": datetime.now(timezone.utc)
                })
            except Exception as e:
                print(f"Error en fila: {e}")
                continue

    return all_data

if __name__ == "__main__":
    datos_criptos = scrape_coinmarketcap_pages(num_pages=5)  
    print(f"Se obtuvieron {len(datos_criptos)} criptomonedas.")
    insert_crypto_data(datos_criptos)

# Este código está bajo licencia MIT.
# (c) 2025 Rebeca Pedrozo Cueto

import os
from dotenv import load_dotenv
from pymongo import MongoClient
import pandas as pd
import streamlit as st

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "e_trading")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def get_all_cryptos():
    collection = db["cryptos"]
    data = list(collection.find())
    if not data:
        return pd.DataFrame()
    
    processed = []
    for doc in data:
        name = doc.get("name", "")
        symbol = doc.get("symbol", "")
        price_raw = doc.get("price", "0")
        try:
            price = float(price_raw.replace("$", "").replace(",", ""))
        except:
            price = 0.0
        scraped_at = doc.get("scraped_at")
        if scraped_at:
            scraped_at = pd.to_datetime(scraped_at)
        else:
            scraped_at = None
        
        processed.append({
            "name": name,
            "symbol": symbol,
            "price": price,
            "scraped_at": scraped_at
        })
    
    df = pd.DataFrame(processed)
    return df

def main():
    st.title("Dashboard de Precios Criptomonedas")
    
    df = get_all_cryptos()
    
    if df.empty:
        st.warning("No se encontraron datos en la base de datos.")
    else:
        st.write("Datos crudos de la colección:")
        st.dataframe(df)
        
        st.write("Gráfico de precios a lo largo del tiempo:")
        df_sorted = df.sort_values(by="scraped_at")
        st.line_chart(df_sorted.set_index("scraped_at")["price"])

if __name__ == "__main__":
    main()

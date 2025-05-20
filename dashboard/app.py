import os
from dotenv import load_dotenv
from pymongo import MongoClient
import pandas as pd
import streamlit as st

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "e_trading")

# Conexión a MongoDB
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
        return
    
    st.write("Datos crudos de la colección:")
    st.dataframe(df)
    
    # Selector para elegir cripto por nombre o símbolo
    opciones = df["name"].astype(str) + " (" + df["symbol"].astype(str) + ")"
    opcion_seleccionada = st.selectbox("Selecciona una criptomoneda:", opciones)
    
    # Extraer símbolo seleccionado
    simbolo_seleccionado = opcion_seleccionada.split("(")[-1].replace(")","").strip()
    
    # Filtrar datos por símbolo
    df_filtrado = df[df["symbol"] == simbolo_seleccionado].sort_values(by="scraped_at")
    
    if df_filtrado.empty:
        st.warning(f"No hay datos para la criptomoneda {opcion_seleccionada}.")
        return
    
    st.write(f"Gráfico de precios para {opcion_seleccionada}:")
    st.line_chart(df_filtrado.set_index("scraped_at")["price"])

if __name__ == "__main__":
    main()

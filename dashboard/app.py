import os
from dotenv import load_dotenv
from pymongo import MongoClient
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "e_trading")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

BASE_PRICES = {
    "BTC": 28000.00,
    "ETH": 1800.00,
    "USDT": 1.00,
    "XRP": 0.50,
    "ADA": 0.40,
   
}

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
        except Exception:
            price = 0.0
        
        scraped_at_raw = doc.get("scraped_at")
        scraped_at = None
        if scraped_at_raw:
            try:
                if isinstance(scraped_at_raw, dict) and "$date" in scraped_at_raw:
                    scraped_at = pd.to_datetime(scraped_at_raw["$date"])
                else:
                    scraped_at = pd.to_datetime(scraped_at_raw)
            except Exception:
                scraped_at = None
        
        processed.append({
            "name": name,
            "symbol": symbol,
            "price": price,
            "scraped_at": scraped_at
        })
    
    df = pd.DataFrame(processed)
    return df.dropna(subset=["scraped_at"])

def add_base_prices(df):
    base_date = datetime.utcnow() - timedelta(days=7)
    base_data = []
    for symbol in df["symbol"].unique():
        if symbol in BASE_PRICES:
            base_data.append({
                "name": "",
                "symbol": symbol,
                "price": BASE_PRICES[symbol],
                "scraped_at": base_date
            })
    if base_data:
        df_base = pd.DataFrame(base_data)
        df = pd.concat([df, df_base], ignore_index=True)
        df = df.sort_values(by=["symbol", "scraped_at"]).reset_index(drop=True)
    return df

def main():
    st.set_page_config(page_title="Crypto Tracker", layout="wide")

    st.markdown(
        "<h1 style='text-align: center; color: #00aaff;'>📈 Dashboard de Criptomonedas</h1>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    
    df = get_all_cryptos()
    if df.empty:
        st.warning(" No se encontraron datos en la base de datos.")
        return

    df = add_base_prices(df)

    with st.expander(" Ver datos crudos", expanded=False):
        st.dataframe(df, use_container_width=True)

    st.markdown("###  Selecciona una criptomoneda para visualizar su evolución:")
    opciones = []
    symbols_seen = set()
    for _, row in df.iterrows():
        if row["symbol"] not in symbols_seen:
            nombre = row["name"] if row["name"] else row["symbol"]
            opciones.append(f"{nombre} ({row['symbol']})")
            symbols_seen.add(row["symbol"])

    opcion_seleccionada = st.selectbox("Criptomoneda:", opciones)
    simbolo_seleccionado = opcion_seleccionada.split("(")[-1].replace(")", "").strip()

    df_filtrado = df[df["symbol"] == simbolo_seleccionado].sort_values(by="scraped_at")
    if df_filtrado.empty:
        st.warning(f"No hay datos para {opcion_seleccionada}.")
        return

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"###  Gráfico de precios: **{opcion_seleccionada}**")
        st.line_chart(df_filtrado.set_index("scraped_at")["price"])
    with col2:
        latest = df_filtrado.iloc[-1]
        change = ((latest["price"] - BASE_PRICES.get(simbolo_seleccionado, latest["price"])) / BASE_PRICES.get(simbolo_seleccionado, 1)) * 100
        st.metric(
            label="💰 Precio actual",
            value=f"${latest['price']:,.2f}",
            delta=f"{change:.2f}%" if change != 0 else "Sin cambio",
            delta_color="normal" if change == 0 else ("inverse" if change < 0 else "off")
        )
        st.write("Última actualización:", latest["scraped_at"].strftime("%Y-%m-%d %H:%M:%S"))

    st.markdown("---")
    st.markdown(
        "<footer style='text-align: center; font-size: 0.9em;'>Desarrollado con Python, Streamlit y MongoDB</footer>",
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    main()
#/home/codespace/.python/current/bin/python3 -m pip install streamlit
#python -m streamlit run /workspaces/E-trading/dashboard/app.py
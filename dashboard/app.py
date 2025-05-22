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

def get_crypto_data():
    collection = db["cryptos"]
    data = list(collection.find())
    if not data:
        return pd.DataFrame()

    rows = []
    for doc in data:
        try:
            price = float(str(doc.get("price", "0")).replace("$", "").replace(",", ""))
        except:
            price = 0.0

        date = doc.get("scraped_at")
        if isinstance(date, dict) and "$date" in date:
            date = pd.to_datetime(date["$date"])
        else:
            try:
                date = pd.to_datetime(date) 
            except:
                date = None

        if date:
            rows.append({
                "name": doc.get("name", ""),
                "symbol": doc.get("symbol", ""),
                "price": price,
                "scraped_at": date
            })

    df = pd.DataFrame(rows)
    return df

# Interfaz principal
def main():
    st.set_page_config(page_title="Crypto OLAP Dashboard", layout="wide")
    st.title("OLAP de Criptomonedas")

    df = get_crypto_data()
    if df.empty:
        st.error("No se encontraron datos.")
        return

    df["date"] = df["scraped_at"].dt.date
    df["week"] = df["scraped_at"].dt.strftime('%Y-%U')
    df["month"] = df["scraped_at"].dt.strftime('%Y-%m')

    symbols = sorted(df["symbol"].unique())
    st.sidebar.header("Filtros OLAP")

    cryptos_seleccionadas = st.sidebar.multiselect("Criptomonedas:", options=symbols, default=symbols[:3])
    rango_fechas = st.sidebar.date_input(
        "Rango de fechas:",
        [df["scraped_at"].min().date(), df["scraped_at"].max().date()]
    )

    # Validación del rango de fechas
    if len(rango_fechas) != 2 or rango_fechas[0] == rango_fechas[1] or rango_fechas[0] > rango_fechas[1]:
        st.warning("Por favor selecciona un rango de fechas válido (mínimo dos días diferentes y en orden correcto).")
        return

    df_filtrado = df[
        (df["symbol"].isin(cryptos_seleccionadas)) &
        (df["date"] >= rango_fechas[0]) &
        (df["date"] <= rango_fechas[1])
    ]

    if df_filtrado.empty:
        st.warning("No hay datos para los filtros seleccionados.")
        return

    st.subheader(" Promedio Diario de Precios")
    tabla_diaria = df_filtrado.groupby(["date", "symbol"]).agg({"price": "mean"}).reset_index()
    tabla_pivot = tabla_diaria.pivot(index="date", columns="symbol", values="price")
    st.line_chart(tabla_pivot)

    st.subheader("Promedios Semanales")
    weekly = df_filtrado.groupby(["week", "symbol"]).agg({"price": "mean"}).reset_index()
    weekly_pivot = weekly.pivot(index="week", columns="symbol", values="price")
    st.dataframe(weekly_pivot, use_container_width=True)

    st.subheader(" Promedios Mensuales")
    monthly = df_filtrado.groupby(["month", "symbol"]).agg({"price": "mean"}).reset_index()
    monthly_pivot = monthly.pivot(index="month", columns="symbol", values="price")
    st.dataframe(monthly_pivot, use_container_width=True)

    st.subheader(" Cambios porcentuales respecto al precio base")
    cambios = []
    for symbol in cryptos_seleccionadas:
        latest = df_filtrado[df_filtrado["symbol"] == symbol].sort_values("scraped_at").iloc[-1]
        base = BASE_PRICES.get(symbol, latest["price"])
        cambio = ((latest["price"] - base) / base) * 100
        cambios.append((symbol, latest["price"], cambio))

    for s, p, c in cambios:
        st.metric(f"{s} - Precio actual", f"${p:,.2f}", f"{c:.2f}%")

    st.markdown("---")
    st.caption("(c) 2025 Rebeca Pedrozo Cueto")

if __name__ == "__main__":
    main()
#/home/codespace/.python/current/bin/python3 -m pip install streamlit
#python -m streamlit run /workspaces/E-trading/dashboard/app.py
#pip install pandas streamlit pymongo python-dotenv
# Este código está bajo licencia MIT.
# (c) 2025 Rebeca Pedrozo Cueto

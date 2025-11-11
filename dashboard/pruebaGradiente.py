import os
from dotenv import load_dotenv
from pymongo import MongoClient
import pandas as pd
import streamlit as st
import numpy as np
from datetime import datetime
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "e_trading")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
cryptos_col = db["cryptos"]


BASE_PRICES = {
    "BTC": 28000.00,
    "ETH": 1800.00,
    "USDT": 1.00,
    "XRP": 0.50,
    "ADA": 0.40,
}

def get_crypto_data():
    data = list(db["cryptos"].find())
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

    return pd.DataFrame(rows)


def entrenar_modelo(data, window=10):
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data.reshape(-1, 1))

    X, y = [], []
    for i in range(window, len(scaled_data)):
        X.append(scaled_data[i - window:i])
        y.append(scaled_data[i])

    if len(X) == 0:
        raise ValueError("Datos insuficientes para crear ventanas de entrenamiento")

    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(X.shape[1], 1)),
        LSTM(50),
        Dense(1)
    ])

    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X, y, epochs=10, batch_size=32, verbose=0)

    return model, scaler

def predecir_precio(model, scaler, data, window=10):
    last_window = data[-window:]
    scaled_last_window = scaler.transform(last_window.reshape(-1, 1))
    X_test = np.reshape(scaled_last_window, (1, window, 1))
    scaled_pred = model.predict(X_test)
    pred = scaler.inverse_transform(scaled_pred)
    return pred[0][0]

# ==============================
# ACA ESTA LO DEL GRADIENTE!
# ==============================
def descenso_gradiente(data, lr=0.0001, epochs=500):
    """
    Ajusta una línea (modelo lineal) a los datos usando descenso de gradiente.
    """
    x = np.arange(len(data))
    y = np.array(data)

    m, b = 0.0, np.mean(y)

    for _ in range(epochs):
        y_pred = m * x + b
        dm = (-2 / len(x)) * np.sum(x * (y - y_pred))
        db = (-2 / len(x)) * np.sum(y - y_pred)
        m -= lr * dm
        b -= lr * db

    # Predicción del siguiente punto
    next_x = len(x)
    next_y = m * next_x + b
    return next_y, m, b


def main():
    st.set_page_config(page_title="Crypto OLAP Dashboard + Predicción LSTM / Gradiente", layout="wide")

    st.markdown(
        """
        <style>
        .top-right-logo {
            position: fixed;
            top: 10px;
            right: 20px;
            width: 120px;
            height: auto;
            z-index: 1000;
        }
        </style>
        <img src="https://raw.githubusercontent.com/rebeca07-pedrozo/E-crypto/main/pics/cryptoLogo.png" class="top-right-logo">
        """,
        unsafe_allow_html=True,
    )

    st.title("OLAP de Criptomonedas con Predicción Inteligente")

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

    metodo_pred = st.sidebar.radio(
        "Método de predicción:",
        ["LSTM (profundo)", "Sistema Gradiente"]
    )

    if len(rango_fechas) != 2 or rango_fechas[0] >= rango_fechas[1]:
        st.warning("Selecciona un rango de fechas válido.")
        return

    df_filtrado = df[
        (df["symbol"].isin(cryptos_seleccionadas)) &
        (df["date"] >= rango_fechas[0]) &
        (df["date"] <= rango_fechas[1])
    ]

    if df_filtrado.empty:
        st.warning("No hay datos para los filtros seleccionados.")
        return

    st.subheader("Promedio Diario de Precios")
    tabla_diaria = df_filtrado.groupby(["date", "symbol"]).agg({"price": "mean"}).reset_index()
    tabla_pivot = tabla_diaria.pivot(index="date", columns="symbol", values="price")
    st.line_chart(tabla_pivot)

    st.subheader("Promedios Mensuales")
    monthly = df_filtrado.groupby(["month", "symbol"]).agg({"price": "mean"}).reset_index()
    monthly_pivot = monthly.pivot(index="month", columns="symbol", values="price")
    st.dataframe(monthly_pivot, use_container_width=True)

    # --- Predicciones ---
    st.markdown("---")
    st.subheader(f"Predicción y recomendación ({metodo_pred})")

    WINDOW_SIZE = 10

    for symbol in cryptos_seleccionadas:
        datos_symbol = tabla_diaria[tabla_diaria["symbol"] == symbol].sort_values("date")
        precios = datos_symbol["price"].values

        if len(precios) <= WINDOW_SIZE:
            st.write(f"No hay suficientes datos para {symbol}.")
            continue

        try:
            if metodo_pred == "LSTM (profundo)":
                model, scaler = entrenar_modelo(precios, window=WINDOW_SIZE)
                prediccion = predecir_precio(model, scaler, precios, window=WINDOW_SIZE)
            else:
                prediccion, m, b = descenso_gradiente(precios)

            ultimo_precio = precios[-1]
            diferencia = prediccion - ultimo_precio
            porcentaje_cambio = (diferencia / ultimo_precio) * 100

            if porcentaje_cambio > 0:
                recomendacion = "Considera invertir: se espera subida."
            else:
                recomendacion = "Precaución: se espera bajada."

            st.write(f"**{symbol}:** Último = ${ultimo_precio:,.2f}, Predicción = ${prediccion:,.2f} ({porcentaje_cambio:.2f}%)")
            st.write(recomendacion)
            st.markdown("---")

        except Exception as e:
            st.write(f"No se pudo generar la predicción para {symbol}: {e}")

    st.caption("(c) 2025 Rebeca Pedrozo Cueto")

if __name__ == "__main__":
    main()

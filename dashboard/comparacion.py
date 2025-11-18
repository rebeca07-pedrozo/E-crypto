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

#  CONFIG BASE
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

# ESTILO TIPO BINANCE 
st.markdown(
    """
<style>

:root {
    --main-bg: #0d1117;
    --card-bg: #11151c;
    --neon-green: #00ff99;
    --text-main: #e6e6e6;
}

body {
    background-color: var(--main-bg);
}

[data-testid="stAppViewContainer"] {
    background-color: var(--main-bg);
}

[data-testid="stHeader"] {
    background-color: rgba(0,0,0,0);
}

h1, h2, h3, h4, h5, h6, label, span, p {
    color: var(--text-main) !important;
}

.stMetric {
    background: var(--card-bg) !important;
    border-radius: 10px;
    padding: 12px;
    border: 1px solid #222;
}

.css-1q8dd3e {
    color: var(--neon-green) !important;
    font-weight: 700 !important;
}

</style>
""",
    unsafe_allow_html=True
)

#  FUNCIONES DB 
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

#  MODELOS 

def entrenar_modelo(data, window=10):
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data.reshape(-1, 1))

    X, y = [], []
    for i in range(window, len(scaled_data)):
        X.append(scaled_data[i - window:i])
        y.append(scaled_data[i])

    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(window, 1)),
        LSTM(50),
        Dense(1)
    ])

    model.compile(optimizer="adam", loss="mean_squared_error")
    model.fit(X, y, epochs=10, batch_size=32, verbose=0)

    return model, scaler

def predecir_precio(model, scaler, arr, window=10):
    last_window = arr[-window:]
    scaled = scaler.transform(last_window.reshape(-1, 1))
    X_test = np.reshape(scaled, (1, window, 1))
    pred_scaled = model.predict(X_test)
    return scaler.inverse_transform(pred_scaled)[0][0]

def descenso_gradiente(data, lr=0.0001, epochs=500):
    x = np.arange(len(data))
    y = np.array(data)

    m, b = 0.0, np.mean(y)

    for _ in range(epochs):
        y_pred = m * x + b
        dm = (-2 / len(x)) * np.sum(x * (y - y_pred))
        db = (-2 / len(x)) * np.sum(y - y_pred)
        m -= lr * dm
        b -= lr * db

    next_x = len(x)
    next_y = m * next_x + b
    return next_y, m, b

def comparar_modelos(data, window=10):
    precios = np.array(data)

    model, scaler = entrenar_modelo(precios, window)
    pred_lstm = []

    for i in range(window, len(precios)):
        pred = predecir_precio(model, scaler, precios[:i], window)
        pred_lstm.append(pred)

    pred_lstm = [None] * window + pred_lstm

    pred_grad = []
    for i in range(window, len(precios)):
        pred, _, _ = descenso_gradiente(precios[:i])
        pred_grad.append(pred)

    pred_grad = [None] * window + pred_grad

    return pred_lstm, pred_grad


#STREAMLIT APP 
def main():

    st.set_page_config(page_title="E-CRYPTO", layout="wide")

    st.title("Crypto Dashboard general")

    df = get_crypto_data()

    if df.empty:
        st.error(" No se encontraron datos")
        return

    df["date"] = df["scraped_at"].dt.date
    df["week"] = df["scraped_at"].dt.strftime('%Y-%U')
    df["month"] = df["scraped_at"].dt.strftime('%Y-%m')

    symbols = sorted(df["symbol"].unique())

    #  SIDEBAR 
    st.sidebar.header("Filtros")
    cryptos = st.sidebar.multiselect("Criptos:", symbols, default=symbols[:3])

    rango = st.sidebar.date_input("Rango:", [
        df["scraped_at"].min().date(),
        df["scraped_at"].max().date()
    ])

    metodo_pred = "Ambos"  

    df_filtro = df[
        (df["symbol"].isin(cryptos)) &
        (df["date"] >= rango[0]) &
        (df["date"] <= rango[1])
    ]

    tabla = df_filtro.groupby(["date", "symbol"])["price"].mean().reset_index()
    pivot = tabla.pivot(index="date", columns="symbol", values="price")

    st.subheader("Evolución de Precios")
    st.line_chart(pivot)

    st.markdown("---")

    # COMPARAR MODELOS
    st.subheader("Comparación LSTM vs Gradiente")

    simbolo = st.selectbox("Cripto a evaluar:", symbols)

    df_sym = tabla[tabla["symbol"] == simbolo].sort_values("date")

    if len(df_sym) > 15:

        precios = df_sym["price"].values

        pred_lstm, pred_grad = comparar_modelos(precios)

        #  PRED FINAL 
        ultimo_precio = precios[-1]
        pred_final_lstm = pred_lstm[-1]
        pred_final_grad = pred_grad[-1]

        cambio_lstm = ((pred_final_lstm - ultimo_precio) / ultimo_precio) * 100
        cambio_grad = ((pred_final_grad - ultimo_precio) / ultimo_precio) * 100

        msg_lstm = "📈 LSTM sugiere subida" if cambio_lstm > 0 else "📉 LSTM predice bajada"
        msg_grad = "📈 Gradiente sugiere subida" if cambio_grad > 0 else "📉 Gradiente predice bajada"

        if (cambio_lstm > 0 and cambio_grad > 0) or (cambio_lstm < 0 and cambio_grad < 0):
            final_msg = "🟢 Ambos modelos coinciden"
        else:
            final_msg = "🟡 Los modelos NO se ponen de acuerdo"

        st.info(f"""
### 🔍 Análisis final para **{simbolo}**

**Precio actual:**  ${ultimo_precio:,.2f}

| Modelo | Predicción | Cambio | Dirección |
|--------|-----------|--------|-----------|
|  **LSTM** | ${pred_final_lstm:,.2f} | {cambio_lstm:.2f}% | {msg_lstm} |
|  **Gradiente** | ${pred_final_grad:,.2f} | {cambio_grad:.2f}% | {msg_grad} |

---

###  **Resultado:**  
 **{final_msg}**
""")

        comparar_df = pd.DataFrame({
            "date": df_sym["date"],
            "Real": precios,
            "Gradiente": pred_grad,
            "LSTM": pred_lstm,
        })

        st.line_chart(comparar_df.set_index("date"))

    else:
        st.warning("⚠️ No hay suficientes datos para comparar modelos")

    st.caption("© 2025 - Rebeca Pedrozo Cueto")

if __name__ == "__main__":
    main()

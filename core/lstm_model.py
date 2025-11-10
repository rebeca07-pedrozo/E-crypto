import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler

def entrenar_modelo(data, window=10):
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data.reshape(-1, 1))

    X, y = [], []
    for i in range(window, len(scaled_data)):
        X.append(scaled_data[i-window:i])
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

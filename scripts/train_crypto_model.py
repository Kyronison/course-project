from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import yfinance as yf
from keras.src.layers import LSTM, Dropout
from sklearn.preprocessing import MinMaxScaler
from keras import Sequential
import tensorflow as tf
import numpy as np
from tensorflow.python.keras.layers import Dense


def load_data(ticker):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5 * 365)
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)
    df = df[['Close']].rename(columns={'Close': 'close'})
    df['log_close'] = np.log(df['close'])
    df['diff_log'] = df['log_close'].diff().fillna(0)
    return df


def create_sequences(data, n_steps=60, n_future=30):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled = scaler.fit_transform(data[['diff_log']])
    X, y = [], []
    for i in range(n_steps, len(scaled) - n_future):
        X.append(scaled[i - n_steps:i])
        y.append(scaled[i:i + n_future])
    return np.array(X), np.array(y), scaler


def build_model(n_steps=60, n_future=30):
    model = Sequential([
        LSTM(128, return_sequences=True, input_shape=(n_steps, 1)),
        Dropout(0.3),
        LSTM(64, return_sequences=True),
        Dropout(0.2),
        LSTM(32),
        Dense(n_future)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')  # Используйте строку 'mse'
    return model



def train_and_save(ticker, model_save_path, epochs=10, batch_size=32, n_steps=60, n_future=30):
    df = load_data(ticker)
    X, y, scaler = create_sequences(df, n_steps, n_future)
    model = build_model(n_steps, n_future)
    model.fit(X, y, epochs=epochs, batch_size=batch_size, validation_split=0.2, verbose=1)

    # Сохранение модели (весь экземпляр модели)
    model.save(model_save_path)
    # Также можно сохранить scaler отдельно (например, через pickle)
    import pickle
    with open(model_save_path.replace('.h5', '_scaler.pkl'), 'wb') as f:
        pickle.dump(scaler, f)
    print(f"Модель и scaler успешно сохранены в {model_save_path} и {model_save_path.replace('.h5', '_scaler.pkl')}")


if __name__ == '__main__':
    train_and_save('BTC-USD', '../models/trained_models/btc_model.h5')

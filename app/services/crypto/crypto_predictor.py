from datetime import datetime, timedelta
import numpy as np
import yfinance as yf
from keras.src.saving import load_model
import pickle


def load_data(ticker):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5 * 365)
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)
    df = df[['Close']].rename(columns={'Close': 'close'})
    df['log_close'] = np.log(df['close'])
    df['diff_log'] = df['log_close'].diff().fillna(0)
    return df


def predict_future(ticker, model_path, n_steps=60, n_future=30):
    # Загрузка обученной модели и scaler
    model = load_model(model_path)
    scaler_path = model_path.replace('.h5', '_scaler.pkl')
    with open(scaler_path, 'rb') as f:
        scaler = pickle.load(f)

    df = load_data(ticker)
    # Получаем последнюю последовательность преобразованных данных
    last_sequence = df['diff_log'].values[-n_steps:]
    last_log_price = df['log_close'].iloc[-1]

    # Преобразование последовательности
    scaled_seq = scaler.transform(last_sequence.reshape(-1, 1))
    scaled_seq = scaled_seq[-n_steps:].reshape(1, n_steps, 1)

    predicted_scaled = model.predict(scaled_seq)
    predicted_diff = scaler.inverse_transform(predicted_scaled)

    # Восстановление предсказанных логарифмических цен
    predicted_log = np.cumsum(predicted_diff.flatten()) + last_log_price
    predictions = np.exp(predicted_log)

    # Формирование будущих дат (необходимо для визуализации, если нужно)
    future_dates = [df.index[-1] + timedelta(days=i) for i in range(1, n_future + 1)]
    return future_dates, predictions


if __name__ == '__main__':
    dates, preds = predict_future('BTC-USD', '../../../models/trained_models/btc_model.h5')
    print("Прогноз на ближайшие дни:")
    for d, p in zip(dates, preds):
        print(f"{d.strftime('%Y-%m-%d')}: {p:.2f} USD")

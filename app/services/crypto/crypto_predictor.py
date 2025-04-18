from datetime import datetime, timedelta
import numpy as np
import yfinance as yf
from keras.src.saving import load_model
import pickle


def load_data(ticker):
    """
    Загружает исторические данные по тикеру с Yahoo Finance и выполняет
    необходимую предобработку для модели прогнозирования.

    Преобразования включают расчет натурального логарифма цены закрытия
    и разницы логарифмов цен. Данные загружаются за последние 5 лет.

    Args:
        ticker (str): Тикер актива для загрузки данных.

    Returns:
        pandas.DataFrame: DataFrame с оригинальной ценой закрытия ('close')
                          и преобразованными колонками ('log_close', 'diff_log').
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5 * 365)
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)
    df = df[['Close']].rename(columns={'Close': 'close'})
    df['log_close'] = np.log(df['close'])
    df['diff_log'] = df['log_close'].diff().fillna(0)
    return df


def predict_future(ticker, model_path, n_steps=60, n_future=30):
    """
    Загружает предобученную модель прогнозирования и scaler,
    выполняет прогнозирование будущих цен на основе исторических данных.

    Прогнозирование выполняется на n_future шагов вперед, используя
    последние n_steps преобразованных данных в качестве входной последовательности для модели.

    Args:
        ticker (str): Тикер актива для прогнозирования.
        model_path (str): Путь к файлу обученной модели Keras (.h5).
        n_steps (int): Длина входной последовательности данных для модели. По умолчанию 60.
        n_future (int): Количество шагов (дней) для прогнозирования в будущее. По умолчанию 30.

    Returns:
        tuple: Кортеж из двух элементов:
               - future_dates (list): Список объектов datetime для предсказанных будущих дат.
               - predictions (numpy.array): Массив прогнозируемых цен на будущие даты.
    """
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

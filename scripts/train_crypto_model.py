from datetime import datetime, timedelta
import yfinance as yf
from keras.src.layers import LSTM, Dropout, Dense
from sklearn.preprocessing import MinMaxScaler
from keras.src.models import Sequential
import numpy as np


def load_data(ticker):
    """
    Загружает исторические данные по тикеру с Yahoo Finance и выполняет
    необходимую предобработку для модели прогнозирования.

    Данные загружаются за последние 5 лет. Преобразования включают расчет
    натурального логарифма цены закрытия и разницы логарифмов цен,
    которые часто используются для стабилизации временного ряда.

    Args:
        ticker (str): Тикер актива для загрузки данных (например, 'BTC-USD').

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


def create_sequences(data, n_steps=60, n_future=30):
    """
    Создает последовательности входных данных (X) и соответствующих целевых значений (y)
    из предобработанных данных для обучения LSTM модели.

    Использует MinMaxScaler для нормализации данных 'diff_log'.

    Args:
        data (pandas.DataFrame): DataFrame с предобработанными данными, включая колонку 'diff_log'.
        n_steps (int): Длина каждой входной последовательности X (количество шагов истории). По умолчанию 60.
        n_future (int): Количество шагов в будущее, которое модель должна предсказать (длина целевой последовательности y). По умолчанию 30.

    Returns:
        tuple: Кортеж из трех элементов:
               - X (numpy.array): Массив входных последовательностей формы (количество_образцов, n_steps, 1).
               - y (numpy.array): Массив целевых последовательностей формы (количество_образцов, n_future).
               - scaler (MinMaxScaler): Обученный объект MinMaxScaler, использованный для нормализации.
    """
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled = scaler.fit_transform(data[['diff_log']])
    X, y = [], []
    for i in range(n_steps, len(scaled) - n_future):
        X.append(scaled[i - n_steps:i])
        y.append(scaled[i:i + n_future])
    return np.array(X), np.array(y), scaler


def build_model(n_steps=60, n_future=30):
    """
    Строит и компилирует архитектуру LSTM модели прогнозирования.

    Модель состоит из нескольких слоев LSTM, Dropout для регуляризации
    и выходного Dense слоя для предсказания будущих значений.

    Args:
        n_steps (int): Размерность входной последовательности (количество шагов истории). По умолчанию 60.
        n_future (int): Размерность выходного слоя (количество шагов прогноза в будущее). По умолчанию 30.

    Returns:
        keras.models.Sequential: Скомпилированный экземпляр модели Keras.
    """
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
    """
    Оркестрирует процесс тренировки LSTM модели прогнозирования и сохранения
    модели и обученного scaler'а в файлы.

    Args:
        ticker (str): Тикер актива для тренировки модели.
        model_save_path (str): Путь для сохранения файла обученной модели (.h5).
        epochs (int): Количество эпох тренировки. По умолчанию 10.
        batch_size (int): Размер батча для тренировки. По умолчанию 32.
        n_steps (int): Длина входной последовательности для модели. По умолчанию 60.
        n_future (int): Количество шагов для предсказания. По умолчанию 30.
    """
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

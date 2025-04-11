# Используем официальный Python-образ
FROM python:3.10-slim

# Устанавливаем системные зависимости:
# - libpq-dev: для сборки psycopg2
# - build-essential: общие инструменты сборки (gcc, make и т.д.)
# - git: требуется для сборки некоторых Python пакетов (например, osqp)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq-dev \
        build-essential \
        git \
    # Очищаем кэш apt, чтобы уменьшить размер образа
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория в контейнере
WORKDIR /app

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=apps:create_app \
    FLASK_ENV=development \
    PATH="/root/.local/bin:$PATH"

# Устанавливаем зависимости (сначала requirements.txt, чтобы использовать кеширование)
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Открываем порт Flask
EXPOSE 5000

# Команда по умолчанию (может быть переопределена в docker-compose)
CMD ["flask", "run", "--host=0.0.0.0"]

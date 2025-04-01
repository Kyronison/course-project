# tests/test_routes.py
"""
Этот файл проверяет базовую доступность основных веб-страниц (маршрутов)
вашего приложения. Мы не проверяем здесь сложную логику или внешний вид,
а только то, что страница открывается без ошибок сервера (возвращает код 200 OK).
"""
import pytest

# pytest автоматически передаст сюда фикстуру `test_client` из conftest.py
def test_home_page_status(test_client):
    """Тест: Главная страница '/' должна загружаться успешно (код 200)."""
    print("\nТест: GET /")
    # Используем тестовый клиент для отправки GET-запроса на адрес '/'
    response = test_client.get('/')
    # `assert` - это команда проверки. Если условие ложно, тест считается проваленным.
    # `response.status_code` содержит HTTP-код ответа сервера. 200 означает "OK".
    assert response.status_code == 200, f"Ожидался код 200, получено {response.status_code}"
    # (Опционально) Можно проверить наличие уникального текста на странице,
    # чтобы убедиться, что загрузился правильный HTML.
    # `b''` означает байтовую строку, так как `response.data` возвращает байты.
    # assert b"Ваш заголовок главной страницы" in response.data, "Не найден ожидаемый текст на главной странице"

def test_correlation_page_status(test_client):
    """Тест: Страница '/analytics/correlation' должна загружаться успешно (код 200)."""
    print("\nТест: GET /analytics/correlation")
    # УБЕДИТЕСЬ, что URL '/analytics/correlation' совпадает с тем, что у вас в @app.route(...)
    response = test_client.get('/analytics/correlation')
    assert response.status_code == 200, f"Ожидался код 200, получено {response.status_code}"
    # assert b"Анализ корреляции" in response.data, "Не найден ожидаемый текст на странице корреляции"

def test_portfolio_page_status(test_client):
    """Тест: Страница '/analytics/portfolio' должна загружаться успешно (код 200)."""
    print("\nТест: GET /analytics/portfolio")
    # УБЕДИТЕСЬ, что URL '/analytics/portfolio' совпадает с тем, что у вас в @app.route(...)
    response = test_client.get('/analytics/portfolio')
    assert response.status_code == 200, f"Ожидался код 200, получено {response.status_code}"
    # assert b"Формирование портфеля" in response.data, "Не найден ожидаемый текст на странице портфеля"

# TODO: Добавьте сюда тесты для проверки других страниц вашего приложения, если они есть.
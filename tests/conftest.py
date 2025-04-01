import pytest
from apps import create_app
from app.models.models import db


class TestConfig:
    """Конфигурация Flask для тестов."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    TINKOFF_API_KEY = 'fake_test_key_for_init'


@pytest.fixture(scope='module')
def test_app():
    app = create_app(config_class=TestConfig)
    with app.app_context():
        yield app


@pytest.fixture(scope='module')
def test_client(test_app):
    return test_app.test_client()


@pytest.fixture(scope='function')
def init_database(test_app):
    with test_app.app_context():
        db.create_all()  # Create tables
        yield db
        db.session.remove()
        db.drop_all()

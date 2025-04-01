from datetime import datetime
from flask import Flask, render_template
from config.config import Config
from app.models.models import db
from scripts.database.create_db import create_database_if_not_exists
from apscheduler.schedulers.background import BackgroundScheduler

# Импортируем блюпринт
from app.routes.correlation_routes import correlation_bp
from app.routes.portfolio_routes import portfolio_bp
from app.data.market_data import update_sector_data_in_db
from flask_cors import CORS
from flask import Flask


def create_app(config_class=Config):  # Добавляем параметр с значением по умолчанию
    create_database_if_not_exists()

    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(config_class)  # Используем переданный конфиг

    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5010", "http://127.0.0.1:5010"],
            "methods": ["GET", "POST"],
            "allow_headers": ["Content-Type"]
        }
    })

    db.init_app(app)
    CORS(app)

    # Регистрируем блюпринт
    app.register_blueprint(correlation_bp, url_prefix='/api')

    app.register_blueprint(portfolio_bp, url_prefix='/api')

    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/analytics')
    def analytics_index():
        """
        Страница со списком аналитических инструментов (наши "карточки").
        """
        return render_template('analytics_dashboard.html')

    @app.route('/analytics/correlation')
    def analytics_correlation():
        """
        Страница с конкретным функционалом – анализ корреляций (бывшая analytics.html).
        """
        return render_template('correlation.html')

    @app.route('/analytics/portfolio')
    def analytics_portfolio():
        """
        Страница с конкретным функционалом - формирование портфеля и его ребалансировка.
        """
        return render_template('portfolio.html')

    # Инициализируем планировщик
    scheduler = BackgroundScheduler()
    app.scheduler = scheduler  # Сохраняем планировщик в приложении

    def update_job():
        with app.app_context():
            db.create_all()
            print("Запуск автоматического обновления данных...")
            # companies = [asset['name'] for sector in Config.SECTORS.values() for asset in sector]
            update_sector_data_in_db()

    # Добавляем задачу в планировщик
    scheduler.add_job(
        func=update_job,
        trigger='interval',
        minutes=10,
        next_run_time=datetime.now()
    )

    # Запускаем планировщик только если он еще не запущен
    try:
        scheduler.start()
    except Exception as e:
        print(f"Ошибка при запуске планировщика: {e}")

    @app.teardown_appcontext
    def shutdown_scheduler(exception=None):
        # Безопасное завершение работы планировщика
        scheduler = getattr(app, 'scheduler', None)
        if scheduler is not None and scheduler.state:
            scheduler.shutdown(wait=False)

    return app


if __name__ == '__main__':
    flask_app = create_app()
    flask_app.run(debug=False, host='127.0.0.1', port=5010)

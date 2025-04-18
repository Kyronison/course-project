import psycopg2
import psycopg2.errors
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config.config import Config


def create_database_if_not_exists():
    """
    Подключается к системной базе данных 'postgres' с использованием учетных данных
    суперпользователя или владельца. Проверяет существование целевой базы данных,
    указанной в Config.PG_DB. Если целевая база данных не существует, создает ее.

    Требует соответствующих прав доступа к серверу PostgreSQL.
    """
    db_to_create = Config.PG_DB

    # Подключаемся к системной БД 'postgres', а не к самой 'my_db'
    conn_str = f"postgresql://{Config.PG_USER}:{Config.PG_PASS}@{Config.PG_HOST}:{Config.PG_PORT}/postgres"
    conn = None
    try:
        conn = psycopg2.connect(conn_str)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Проверяем, есть ли база
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_to_create,))
        exists = cursor.fetchone()
        if not exists:
            cursor.execute(f"CREATE DATABASE {db_to_create}")
            print(f"Database '{db_to_create}' created.")
        else:
            print(f"Database '{db_to_create}' already exists.")
        cursor.close()
    except psycopg2.Error as e:
        print("Error while checking/creating database:", e)
    finally:
        if conn:
            conn.close()

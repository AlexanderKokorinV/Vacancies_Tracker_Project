import pytest
import psycopg2
from src.db_manager import DBManager
import os
from pathlib import Path
from dotenv import load_dotenv
from src.hh_api import HHParser

# Прописываем прямой путь к .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)



# Настройки для тестовой БД
TEST_PARAMS = {
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT")
}
TEST_DB_NAME = "test_hh_db"


# Фикстуры для тестов db_manager
@pytest.fixture(scope="module")
def db_setup():
    """Фикстура для создания тестовой БД и таблиц"""
    # Создаем базу
    conn = psycopg2.connect(dbname="postgres", **TEST_PARAMS)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")
    cur.execute(f"CREATE DATABASE {TEST_DB_NAME}")
    cur.close()
    conn.close()

    # Создаем таблицы в тестовой БД
    conn = psycopg2.connect(dbname=TEST_DB_NAME, **TEST_PARAMS)
    with conn.cursor() as cur:
        cur.execute("CREATE TABLE employers (employer_id INT PRIMARY KEY, name VARCHAR(255), url TEXT)")
        cur.execute("""
            CREATE TABLE vacancies (
                vacancy_id SERIAL PRIMARY KEY, 
                employer_id INT REFERENCES employers(employer_id),
                title VARCHAR(255), 
                salary_from INT, 
                salary_to INT,
                url TEXT
            )
        """)
        # Наполняем тестовыми данными
        cur.execute("INSERT INTO employers VALUES (1, 'Test Company')")
        cur.execute("INSERT INTO vacancies (employer_id, title, salary_from, salary_to) VALUES (1, 'Python Dev', 100, 200)")
    conn.commit()
    conn.close()

    yield # Здесь запускаются сами тесты


@pytest.fixture
def manager():
    """Создает экземпляр DBManager для тестов"""
    return DBManager(TEST_DB_NAME, TEST_PARAMS)


# Фикстуры для тестов utils
@pytest.fixture
def test_db_config():
    """Параметры для тестовой среды"""
    return {
        "name": "test_creation_db",
        "params": {
            "user": "postgres",
            "password": os.getenv("DB_PASSWORD"),
            "host": "localhost",
            "port": 5432
        }
    }

@pytest.fixture
def db_connection(db_setup): # Используем созданную ранее фикстуру базы
    """Фикстура для прямого доступа к тестовой БД"""
    conn = psycopg2.connect(dbname="test_hh_db", **TEST_PARAMS)
    yield conn
    conn.close()


@pytest.fixture
def parser():
    """Создает экземпляр HHParser для тестов"""
    return HHParser()
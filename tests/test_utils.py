import os
from typing import Any
from unittest.mock import MagicMock

import psycopg2

from src.db_manager import DBManager
from src.utils import create_database, save_to_db

TEST_PARAMS = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}
TEST_DB_NAME = "test_hh_db"


# Тесты для функции create_database
def test_create_database_success(test_db_config: dict[str, Any]) -> None:
    """Проверка создания базы и таблиц"""
    db_name = test_db_config["name"]
    params = test_db_config["params"]

    # 1. Запускаем создание
    create_database(db_name, params)

    # 2. Проверяем, можно ли подключиться к новой базе
    conn = psycopg2.connect(dbname=db_name, **params)
    cur = conn.cursor()

    # 3. Проверяем наличие таблиц в схеме
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = [row[0] for row in cur.fetchall()]

    assert "employers" in tables
    assert "vacancies" in tables

    # 4. Проверяем колонки в таблице employers
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'employers'")
    columns = [row[0] for row in cur.fetchall()]

    assert "employer_id" in columns
    assert "name" in columns

    cur.close()
    conn.close()


def test_create_database_recreation(test_db_config: dict[str, Any]) -> None:
    """Проверка, что функция корректно пересоздает уже существующую базу"""
    db_name = test_db_config["name"]
    params = test_db_config["params"]

    # Запускаем дважды подряд
    create_database(db_name, params)
    create_database(db_name, params)  # Не должно быть ошибки "Database already exists"


# Тесты для функции save_to_db
def test_save_to_db(db_connection: psycopg2.extensions.connection, manager: DBManager) -> None:
    """Тест сохранения данных в БД"""
    # 1. Создаем тестовые данные (как будто из HH)
    test_data = [{"id": "777", "name": "Super Company", "alternate_url": "http://hh.ru"}]

    # 2. Создаем Mock для HHParser
    mock_hh = MagicMock()
    mock_hh.get_vacancies.return_value = [
        {"name": "Python Developer", "salary": {"from": 100, "to": 200}, "alternate_url": "http://hh.ru"}
    ]

    # 3. Запускаем сохранение
    save_to_db(test_data, "test_hh_db", TEST_PARAMS, mock_hh)

    # 4. Проверяем результаты через курсор
    with db_connection.cursor() as cur:
        # Проверяем работодателя
        cur.execute("SELECT name FROM employers WHERE employer_id = 777")
        res_employer = cur.fetchone()
        assert res_employer is not None, "Работодатель не найден в БД"
        assert res_employer[0] == "Super Company"

        # Проверяем вакансию
        cur.execute("SELECT title, salary_from FROM vacancies WHERE employer_id = 777")
        row = cur.fetchone()
        assert row is not None, "Вакансия не найдена в БД"
        assert row[0] == "Python Developer"
        assert row[1] == 100


def test_save_to_db_none_salary(db_connection: psycopg2.extensions.connection, manager: DBManager) -> None:
    """Тест сохранения вакансии с пустой зарплатой"""
    test_data = [{"id": "888", "name": "No Salary Co", "alternate_url": "url"}]

    mock_hh = MagicMock()
    # Имитируем отсутствие словаря salary (как часто бывает в API HH)
    mock_hh.get_vacancies.return_value = [{"name": "Intern", "salary": None, "alternate_url": "url"}]

    save_to_db(test_data, "test_hh_db", TEST_PARAMS, mock_hh)

    with db_connection.cursor() as cur:
        cur.execute("SELECT salary_from, salary_to FROM vacancies WHERE employer_id = 888")
        row = cur.fetchone()
        assert row[0] is None
        assert row[1] is None

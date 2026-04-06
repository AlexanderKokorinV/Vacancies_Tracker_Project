import psycopg2

from src.hh_api import HHParser


def create_database(db_name: str, params: dict) -> None:
    """Создание базы данных и таблиц vacancies и employers"""
    # Подключаемся к дефолтной базе "postgres", чтобы создать новую БД
    conn = psycopg2.connect(dbname="postgres", **params)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{db_name}'
              AND pid <> pg_backend_pid();
        """)

    # Создаем БД
    cur.execute(f"DROP DATABASE IF EXISTS {db_name}")
    cur.execute(f"CREATE DATABASE {db_name}")

    cur.close()
    conn.close()

    # Подключаемся к созданной БД
    conn = psycopg2.connect(dbname=db_name, **params)
    with conn.cursor() as cur:
        # Таблица работодателей
        cur.execute("""
            CREATE TABLE employers (
                employer_id INT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                url TEXT
            )
        """)

        # Таблица вакансий
        cur.execute("""
            CREATE TABLE vacancies (
                vacancy_id SERIAL PRIMARY KEY,
                employer_id INT REFERENCES employers(employer_id),
                title VARCHAR(255) NOT NULL,
                salary_from INT,
                salary_to INT,
                url TEXT
            )
        """)

    conn.commit()
    conn.close()
    print(f"База данных {db_name} и таблицы созданы.")


def save_to_db(data: list[dict], db_name: str, params: dict, hh: HHParser) -> None:
    """Заполнение данных таблиц vacancies и employers"""

    conn = psycopg2.connect(dbname=db_name, **params)

    with conn.cursor() as cur:

        for employer in data:
            # Сохраняем работодателя
            cur.execute(
                """
                INSERT INTO employers (employer_id, name, url)
                VALUES (%s, %s, %s)
                ON CONFLICT (employer_id) DO NOTHING
                """,
                (employer["id"], employer["name"], employer["alternate_url"]),
            )

            # Получаем вакансии для этого работодателя (используя метод из HHParser)
            vacancies = hh.get_vacancies(employer["id"])

            for vac in vacancies:
                # Обработка зарплаты (может быть None)
                salary = vac.get("salary")  # Получаем словарь salary

                if salary:
                    salary_from = salary.get("from")
                    salary_to = salary.get("to")
                else:
                    salary_from = None
                    salary_to = None

                cur.execute(
                    """
                    INSERT INTO vacancies (employer_id, title, salary_from, salary_to, url)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (employer["id"], vac["name"], salary_from, salary_to, vac["alternate_url"]),
                )

    conn.commit()
    conn.close()

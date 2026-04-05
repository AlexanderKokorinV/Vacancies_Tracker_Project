import psycopg2
from src.utils import *




class DBManager:
    """Класс для работы с данными в БД PostgreSQL"""

    def __init__(self, db_name, params):
        """Конструктор для класса DBManager"""
        self.db_name = db_name
        self.params = params

    def get_companies_and_vacancies_count(self):
        """Получает список всех компаний и количество вакансий у каждой компании"""
        query = """
            SELECT e.name, COUNT(v.vacancy_id) as vacancies_count
            FROM employers AS e
            LEFT JOIN vacancies v ON e.employer_id = v.employer_id
            GROUP BY e.name
            ORDER BY vacancies_count DESC;
        """

        conn = psycopg2.connect(dbname=self.db_name, **self.params)
        with conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchall()

        conn.close()
        return result

    def get_all_vacancies(self):
        """Получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию"""
        query = """
        SELECT e.name, v.title, v.salary_from, v.salary_to, v.url
        FROM vacancies AS v
        JOIN employers e ON v.employer_id = e.employer_id
        ORDER BY e.name;
        """

        conn = psycopg2.connect(dbname=self.db_name, **self.params)
        with conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchall()

        conn.close()
        return result

    def get_avg_salary(self):
        """Получает среднюю зарплату по вакансиям"""
        # Считаем среднее между ОТ и ДО для каждой вакансии, а затем общее среднее по всей таблице
        query = """SELECT AVG((COALESCE(salary_from, salary_to) + COALESCE(salary_to, salary_from)) / 2) 
                   FROM vacancies
                """

        conn = psycopg2.connect(dbname=self.db_name, **self.params)
        with conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchone()
        conn.close()

        if result and result[0] is not None:
            return int(float(result[0]))  # Извлекаем число, превращаем в float, затем в int

        return 0

    def get_vacancies_with_higher_salary(self):
        """Получает список вакансий с зарплатой выше средней по всем вакансиям"""

        avg_salary = self.get_avg_salary()

        query = "SELECT AVG((COALESCE(salary_from, salary_to) + COALESCE(salary_to, salary_from)) / 2) FROM vacancies"

        conn = psycopg2.connect(dbname=self.db_name, **self.params)
        with conn.cursor() as cur:
            cur.execute(query, (avg_salary,))
            result = cur.fetchall()

        conn.close()
        return result

    def get_vacancies_with_keyword(self, keyword):
        """Получает список всех вакансий, в названии которых содержится ключевое слово"""
        query = """
                    SELECT e.name, v.title, v.salary_from, v.salary_to, v.url
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.employer_id
                    WHERE v.title ILIKE %s
                    ORDER BY v.salary_from DESC;
                """

        conn = psycopg2.connect(dbname=self.db_name, **self.params)
        with conn.cursor() as cur:
            # Формируем строку поиска: %слово%
            search_query = f"%{keyword}%"
            cur.execute(query, (search_query,))
            result = cur.fetchall()

        conn.close()
        return result

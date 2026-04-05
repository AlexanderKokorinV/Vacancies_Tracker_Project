import os
from src.utils import *
from src.db_manager import DBManager
from src.hh_api import HHParser
from dotenv import load_dotenv
load_dotenv()

db_params = {
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT")
    }
db_name = "hh_ru_db"



def main():
    """Консольное меню для взаимодействия с пользователем"""

    # Список из 10 интересующих компаний
    companies = ["Yandex", "Ozon", "VK", "Softline", "Rostelecom", "Kaspersky", "Astra", "Aviasales", "Selectel", "Naumen"]

    # 1. Перезаписываем данные в БД при запуске скрипта
    print("Обновление данных из hh.ru... Пожалуйста, подождите.")

    hh = HHParser()

    # Получаем актуальные данные по списку компаний
    employers_data = hh.get_employers(companies)

    # Пересоздаем таблицы и сохраняем новые компании
    create_database(db_name, db_params)
    save_to_db(employers_data, db_name, db_params, hh)

    print("Данные успешно обновлены!")

    # Инициализируем менеджер базы данных
    db_manager = DBManager(db_name, db_params)

    while True:
        print("\nДобро пожаловать в трекер вакансий c сайта hh.ru!")
        print("1. Список компаний и количество вакансий")
        print("2. Все вакансии (с названием компании и ссылкой)")
        print("3. Средняя зарплата по всем вакансиям")
        print("4. Вакансии с зарплатой выше средней")
        print("5. Поиск вакансий по ключевому слову")
        print("0. Выход")

        choice = input("\nВыберите действие (0-5): ")

        if choice == "1":
            companies = db_manager.get_companies_and_vacancies_count()
            print("\nКомпании и количество вакансий:")
            for company in companies:
                print(f"{company[0]}: {company[1]}")

        elif choice == "2":
            vacancies = db_manager.get_all_vacancies()
            print("\nВсе вакансии в базе:")
            for v in vacancies:
                salary = f"{v[2]}-{v[3]}" if v[2] else "не указана"
                print(f"Компания: {v[0]} | Вакансия: {v[1]} | ЗП: {salary} | Ссылка: {v[4]}")

        elif choice == "3":
            avg_salary = db_manager.get_avg_salary()
            print(f"\nСредняя зарплата по всей базе: {avg_salary} руб.")

        elif choice == "4":
            high_vacs = db_manager.get_vacancies_with_higher_salary()
            print(f"\nНайдено {len(high_vacs)} вакансий с ЗП выше средней:")
            for v in high_vacs:
                # Если salary_from равен None, берем salary_to, иначе пишем "не указана"
                s_from = v[2] if v[2] is not None else (v[3] if v[3] is not None else "не указана")
                print(f"Компания: {v[0]} | Вакансия: {v[1]} | ЗП: {s_from} руб.")

        elif choice == "5":
            keyword = input("Введите слово для поиска (например, менеджер): ")
            search_results = db_manager.get_vacancies_with_keyword(keyword)
            print(f"\nРезультаты по запросу '{keyword}':")
            for v in search_results:
                print(f"{v[0]}: {v[1]} | Ссылка: {v[4]}")

        elif choice == "0":
            print("Завершение работы.")
            break

        else:
            print("Ошибка: введите число от 0 до 5.")



if __name__ == "__main__":
    main()




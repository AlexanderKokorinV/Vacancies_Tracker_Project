from src.db_manager import DBManager


def test_get_companies_and_vacancies_count(db_setup: None, manager: DBManager) -> None:
    """Тест подсчета вакансий"""
    result = manager.get_companies_and_vacancies_count()
    assert len(result) == 1
    assert result[0][0] == "Test Company"
    assert result[0][1] == 1  # 1 вакансия


def test_get_avg_salary(db_setup: None, manager: DBManager) -> None:
    """Тест расчета средней зарплаты"""
    result = manager.get_avg_salary()
    assert result == 150  # (100 + 200) / 2 = 150


def test_get_vacancies_with_keyword(db_setup: None, manager: DBManager) -> None:
    """Тест поиска по слову"""
    result = manager.get_vacancies_with_keyword("Python")
    assert len(result) == 1
    assert "Python Dev" in result[0][1]


def test_get_all_vacancies(manager: DBManager, db_setup: None) -> None:
    """Тест получения полного списка вакансий с названиями компаний"""
    # 1. Вызываем метод
    result = manager.get_all_vacancies()

    # 2. Проверяем структуру результата
    assert isinstance(result, list)  # Должен быть список
    assert len(result) >= 1  # В базе есть как минимум 1 тестовая запись

    # 3. Проверяем содержимое первой записи (кортежа)
    first_vac = result[0]

    # Ожидаемый порядок полей: (Name, Title, Salary_From, Salary_To, URL)
    assert first_vac[0] == "Test Company"  # Название компании из таблицы employers
    assert first_vac[1] == "Python Dev"  # Название вакансии из таблицы vacancies
    assert first_vac[2] == 100  # salary_from
    assert first_vac[3] == 200  # salary_to

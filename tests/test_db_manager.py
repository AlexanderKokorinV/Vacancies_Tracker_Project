



def test_get_companies_and_vacancies_count(db_setup, manager):
    """Тест подсчета вакансий"""
    result = manager.get_companies_and_vacancies_count()
    assert len(result) == 1
    assert result[0][0] == "Test Company"
    assert result[0][1] == 1 # 1 вакансия

def test_get_avg_salary(db_setup, manager):
    """Тест расчета средней зарплаты"""
    result = manager.get_avg_salary()
    assert result == 150  # (100 + 200) / 2 = 150

def test_get_vacancies_with_keyword(db_setup, manager):
    """Тест поиска по слову"""
    result = manager.get_vacancies_with_keyword("Python")
    assert len(result) == 1
    assert "Python Dev" in result[0][1]
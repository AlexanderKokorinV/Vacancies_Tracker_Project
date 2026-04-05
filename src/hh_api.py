import requests
import time



class HHParser:
    """Класс для работы с API hh.ru"""
    def __init__(self):
        """Конструктор для класса HHParser"""
        self.base_url = "https://api.hh.ru"
        self.headers = {"User-Agent": "hh_api_db/1.0"}

    def get_employers(self, employer_names: list[str]):
        """Данные о работодателях"""
        employers_data = []
        for name in employer_names:
            params = {
                "text": name,
                "only_with_vacancies": True,
                "type": "company",
                "area": 113,
            }

            response = requests.get(
                f"{self.base_url}/employers", params=params, headers=self.headers
            )

            if response.status_code == 200:
                items = response.json().get("items")
                if items:
                    employers_data.append(items[0])

            time.sleep(0.2)

        return employers_data


    def get_vacancies(self, employer_id: str):
        """Получение вакансий конкретного работодателя"""
        params = {
            "employer_id": employer_id,
            "per_page": 10,
            "only_with_salary": True
        }

        response = requests.get(
            f"{self.base_url}/vacancies", params=params, headers=self.headers
        )

        if response.status_code == 200:
            return response.json().get("items", [])
        return []




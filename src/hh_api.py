import time
from typing import Any

import requests


class HHParser:
    """Класс для работы с API hh.ru"""

    def __init__(self) -> None:
        """Конструктор для класса HHParser"""
        self.base_url = "https://api.hh.ru"
        self.headers = {"User-Agent": "hh_api_db/1.0"}

    def get_employers(self, employer_names: list[str]) -> list[dict]:
        """Данные о работодателях"""
        employers_data = []
        for name in employer_names:
            params: dict[str, Any] = {
                "text": name,
                "only_with_vacancies": True,
                "type": "company",
                "area": 113,
            }

            response = requests.get(f"{self.base_url}/employers", params=params, headers=self.headers)

            if response.status_code == 200:
                items = response.json().get("items")
                if items:
                    employers_data.append(items[0])

            time.sleep(0.2)

        return employers_data

    def get_vacancies(self, employer_id: str) -> list[dict]:
        """Получение вакансий конкретного работодателя"""
        params: dict[str, Any] = {"employer_id": employer_id, "per_page": 10, "only_with_salary": True}

        response = requests.get(f"{self.base_url}/vacancies", params=params, headers=self.headers)

        if response.status_code == 200:
            # Извлекаем данные
            data = response.json()
            items = data.get("items")

            # Проверяем, что items — это действительно список, чтобы успокоить mypy
            if isinstance(items, list):
                return items

        return []

from unittest.mock import MagicMock, patch

from src.hh_api import HHParser


@patch("requests.get")
def test_hh_get_employers_success(mock_get: MagicMock) -> None:
    """Тест успешного поиска работодателя"""
    parser = HHParser()

    # Настраиваем Mock ответа
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"items": [{"id": "1", "name": "Yandex"}]}
    mock_get.return_value = mock_response

    result = parser.get_employers(["Yandex"])

    # Проверяем, что в списке есть наш результат
    assert len(result) > 0
    assert result[0]["name"] == "Yandex"
    mock_get.assert_called_once()


@patch("requests.get")
def test_hh_get_vacancies_empty(mock_get: MagicMock) -> None:
    """Тест случая, когда у компании нет открытых вакансий"""
    parser = HHParser()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"items": []}  # Имитируем пустой список от HH
    mock_get.return_value = mock_response

    # Вызываем метод для любого ID
    result = parser.get_vacancies("999")

    assert result == []

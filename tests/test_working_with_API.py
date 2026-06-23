import pytest
from unittest.mock import MagicMock
from src.working_with_API import *


@pytest.fixture
def mock_requests(monkeypatch):
    """
    Эта фикстура заменяет Session.get() на "заглушку", которая возвращает
    предопределенный ответ вместо реального HTTP-запроса.
    """
    mock_get = MagicMock()
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = None
    mock_response.json.return_value = {"mocked": True}
    mock_get.return_value = mock_response

    monkeypatch.setattr(requests.Session, 'get', mock_get)
    return mock_get


# Тесты для класса NominatimApiClient

def test_nominatim_client_get_data_calls_make_request(mock_requests):
    """Проверяем, что get_data вызывает _make_request с правильными аргументами."""
    client = NominatimApiClient(user_agent="TestAgent")

    result = client.get_data('search', {'country': 'Canada'})

    mock_requests.assert_called_once()
    args, kwargs = mock_requests.call_args
    assert args[0] == "https://nominatim.openstreetmap.org/search"
    assert kwargs['params'] == {'country': 'Canada'}

    assert result == {"mocked": True}


def test_nominatim_client_get_country_bounding_box_not_found(mock_requests):
    """Проверяем поведение, если страна не найдена."""
    mock_requests.return_value.json.return_value = []

    client = NominatimApiClient(user_agent="TestAgent")
    bbox = client.get_country_bounding_box("NonExistentCountry")

    assert bbox is None


# Тесты для класса OpenSkyApiClient

def test_opensky_client_get_aircraft_in_area(mock_requests):
    """Проверяем формирование запроса к OpenSky API."""
    client = OpenSkyApiClient()
    result = client.get_aircraft_in_area(45, 60, -140, -50, time=1620000000)

    mock_requests.assert_called_once()
    args, kwargs = mock_requests.call_args
    expected_url = "https://opensky-network.org/api/states/all"
    assert args[0] == expected_url

    params = kwargs['params']
    assert params['lamin'] == 45
    assert params['lamax'] == 60
    assert params['lomin'] == -140
    assert params['lomax'] == -50
    assert params['time'] == 1620000000

    # Проверяем результат
    assert result == {"mocked": True}
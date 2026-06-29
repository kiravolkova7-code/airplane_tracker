import pytest
from src.working_with_API import NominatimApiClient, OpenSkyApiClient


# Тесты для NominatimApiClient
def test_nominatim_client_get_data_calls_make_request(mocker):
    """Проверяет, что get_data формирует правильный URL и параметры."""

    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"mocked": True}

    mock_session_get = mocker.patch('requests.Session.get', return_value=mock_response)

    client = NominatimApiClient(user_agent="TestAgent")
    result = client.get_data('search', {'country': 'Canada'})
    mock_session_get.assert_called_once()
    args, kwargs = mock_session_get.call_args

    assert args[0] == "https://nominatim.openstreetmap.org/search"
    assert kwargs['params'] == {'country': 'Canada'}
    assert result == {"mocked": True}


# Тесты для OpenSkyApiClient
def test_opensky_get_aircraft_in_area_success(mocker):
    """Успешный запрос списка самолетов."""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "states": [
            ["aabbcc", "URAL123", "RUS", 10000, None, 55.75, 37.62, None, None, 800],
            ["ddeeff", "S78901", "RUS", 11000, None, 59.75, 30.32, None, None, 850]
        ]
    }

    mocker.patch('requests.get', return_value=mock_response)
    client = OpenSkyApiClient()
    aircraft_list = client.get_aircraft_in_area(lamin=50, lamax=60, lomin=30, lomax=40)

    assert len(aircraft_list) == 2
    assert aircraft_list[0].callsign == "URAL123"
    assert aircraft_list[1].altitude == 11000.0


def test_opensky_get_aircraft_in_area_http_error(mocker):
    """Обработка ошибки HTTP (например, 400 Bad Request)."""
    mock_response = mocker.Mock()
    mock_response.status_code = 400
    mock_response.raise_for_status.side_effect = Exception("Bad Request")

    mocker.patch('requests.get', return_value=mock_response)

    client = OpenSkyApiClient()

    with pytest.raises(Exception, match="Bad Request"):
        client.get_aircraft_in_area(lamin=50, lamax=60, lomin=30, lomax=40)


def test_opensky_get_aircraft_in_area_empty_response(mocker):
    """
    Тест обработки пустого ответа от API (когда нет данных о самолетах).
    """
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"other_key": "value"}

    mocker.patch('requests.get', return_value=mock_response)

    client = OpenSkyApiClient()
    aircraft_list = client.get_aircraft_in_area(lamin=50, lamax=60, lomin=30, lomax=40)

    assert len(aircraft_list) == 0


def test_opensky_get_aircraft_in_area_invalid_plane_data(mocker, capsys):
    """
    Тест обработки списка, где один самолет валидный, а другой - нет.
    Проверяет ветку try-except ValueError при создании объекта AirplaneInfo.
    """
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "states": [
            ["valid_icao", "VALID123", "RUS", 10000, None, 55.75, 37.62, None, None, 900], # Валидный борт
            ["invalid_icao", "INVALID", "RUS", -500, None, 55.75, 37.62, None, None, 900]   # Неверная высота (-500)
        ]
    }

    mocker.patch('requests.get', return_value=mock_response)

    client = OpenSkyApiClient()
    aircraft_list = client.get_aircraft_in_area(lamin=50, lamax=60, lomin=30, lomax=40)

    captured = capsys.readouterr()
    assert "[DEBUG] Пропущен самолет с некорректными данными:" in captured.out

    assert len(aircraft_list) == 1
    assert aircraft_list[0].callsign == "VALID123"

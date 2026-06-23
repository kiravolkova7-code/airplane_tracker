import pytest
from unittest.mock import MagicMock
from src.working_with_API import NominatimApiClient, OpenSkyApiClient
import requests


@pytest.fixture
def mock_nominatim_requests(monkeypatch):
    mock_get = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {"mocked": True}
    mock_response.raise_for_status.side_effect = None
    mock_get.return_value = mock_response

    monkeypatch.setattr(requests.Session, 'get', mock_get)
    return mock_get


@pytest.fixture
def mock_opensky_requests(monkeypatch):
    mock_get = MagicMock()
    mock_response = MagicMock()

    mock_response.json.return_value = {"other_key": "some_value"}

    mock_response.raise_for_status.side_effect = None
    mock_get.return_value = mock_response

    monkeypatch.setattr(requests.Session, 'get', mock_get)
    return mock_get


# Тесты для NominatimApiClient
def test_nominatim_client_get_data_calls_make_request(mock_nominatim_requests):
    client = NominatimApiClient(user_agent="TestAgent")

    result = client.get_data('search', {'country': 'Canada'})

    mock_nominatim_requests.assert_called_once()
    args, kwargs = mock_nominatim_requests.call_args

    assert args[0] == "https://nominatim.openstreetmap.org/search"
    assert kwargs['params'] == {'country': 'Canada'}

    assert result == {"mocked": True}


# Тест для класса OpenSkyApiClient
def test_opensky_client_get_aircraft_in_area(mock_opensky_requests):
    client = OpenSkyApiClient()

    result = client.get_aircraft_in_area(45, 60, -140, -50, time=1620000000)

    mock_opensky_requests.assert_called_once()
    args, kwargs = mock_opensky_requests.call_args

    expected_url = "https://opensky-network.org/api/states/all"
    assert args[0] == expected_url

    params = kwargs['params']
    assert params['lamin'] == 45
    assert params['lamax'] == 60
    assert params['lomin'] == -140
    assert params['lomax'] == -50
    assert params['time'] == 1620000000
    assert result == []

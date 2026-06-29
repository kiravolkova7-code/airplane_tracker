import pytest
from src.airplane_info import AirplaneInfo, JsonAirplaneStorage

# Тестовые данные
VALID_PLANE_DATA = [
    "aabbcc",  # ICAO24
    "ACME123",  # CALLSIGN
    None,  # COUNTRY - специально оставляем None, чтобы проверить дефолтное значение
    10000,  # ALTITUDE
    None,
    -75.5,  # LONGITUDE
    45.0,  # LATITUDE
    None,
    None,
    800  # SPEED
]

INCOMPLETE_PLANE_DATA = [None] * 10


#  Фикстуры
@pytest.fixture
def sample_plane_data():
    return {
        "icao24": "a1b2c3",
        "callsign": "AAL123",
        "country": "United States",
        "latitude": 37.0,
        "longitude": -97.0,
        "altitude": 10000.0,
        "speed": 450.0,
    }


@pytest.fixture
def sample_plane_object(sample_plane_data):
    return AirplaneInfo.from_dict(sample_plane_data)


@pytest.fixture
def temp_storage(tmp_path):
    temp_file = tmp_path / f"test_{tmp_path.name}.json"
    storage = JsonAirplaneStorage(filename=str(temp_file))
    return storage


def test_validation_invalid_speed():
    """Тест внутренней валидации: ValueError при отрицательной скорости."""
    data = VALID_PLANE_DATA.copy()
    data[9] = -100
    with pytest.raises(ValueError) as excinfo:
        plane = AirplaneInfo(data)
    assert "Недопустимое значение скорости" in str(excinfo.value)


def test_validation_invalid_altitude():
    """Тест внутренней валидации: ValueError при отрицательной высоте."""
    data = VALID_PLANE_DATA.copy()
    data[3] = -500
    with pytest.raises(ValueError) as excinfo:
        plane = AirplaneInfo(data)
    assert "Недопустимое значение высоты" in str(excinfo.value)


def test_initialization_with_malformed_data():
    """
    Тест устойчивости конструктора к ошибкам TypeError/ValueError.
    Передаем объект, который вызовет AttributeError при len(), покрывая ветку except.
    """
    malformed_data = object()

    plane = AirplaneInfo(malformed_data)

    assert plane.icao24 == "N/A"
    assert plane.callsign == "N/A"
    assert plane.latitude == 0.0
    assert plane.longitude == 0.0
    assert plane.altitude == 0.0
    assert plane.speed == 0.0


def test_json_storage_handles_corrupted_file(tmp_path):
    """Тест устойчивости хранилища к поврежденным JSON-файлам."""
    corrupt_file = tmp_path / "corrupt.json"
    with open(corrupt_file, 'w') as f:
        f.write("{invalid json content}")

    storage = JsonAirplaneStorage(filename=str(corrupt_file))
    result = storage.get_airplane_info()
    assert result == []


def test_successful_initialization():
    """Тест: объект создается успешно и атрибуты заполнены верно."""
    plane = AirplaneInfo(VALID_PLANE_DATA)

    assert plane.icao24 == "aabbcc"
    assert plane.callsign == "ACME123"
    assert plane.country == "N/A"
    assert plane.longitude == -75.5
    assert plane.latitude == 45.0
    assert plane.altitude == 10000.0
    assert plane.speed == 800.0


def test_initialization_with_incomplete_data():
    """Тест: объект создается с дефолтными значениями, если данных не хватает."""
    plane = AirplaneInfo(INCOMPLETE_PLANE_DATA)

    assert plane.callsign == "N/A"
    assert plane.icao24 == "N/A"
    assert plane.country == "N/A"
    assert plane.longitude == 0.0
    assert plane.latitude == 0.0
    assert plane.altitude == 0.0
    assert plane.speed == 0.0


def test_comparison_operators():
    """Тест: операторы сравнения (<, >, ==) работают на основе высоты."""
    data_high = VALID_PLANE_DATA.copy()
    data_high[3] = 10000

    data_low = VALID_PLANE_DATA.copy()
    data_low[3] = 5000

    plane_high = AirplaneInfo(data_high)
    plane_low = AirplaneInfo(data_low)

    assert plane_high > plane_low
    assert plane_low < plane_high
    same_plane = AirplaneInfo(data_high)
    assert plane_high == same_plane


def test_add_and_get_airplane(temp_storage, sample_plane_object):
    """Базовый тест CRUD операции Create & Read."""
    temp_storage.add_airplane_info(sample_plane_object)
    found_planes = temp_storage.get_airplane_info(icao24="a1b2c3")

    assert len(found_planes) == 1
    assert found_planes[0].callsign == sample_plane_object.callsign


def test_prevent_duplicates(temp_storage, sample_plane_object):
    """Проверка уникальности записей."""
    temp_storage.add_airplane_info(sample_plane_object)
    temp_storage.add_airplane_info(sample_plane_object)

    planes = temp_storage.get_airplane_info()
    assert len(planes) == 1


def test_delete_airplane(temp_storage, sample_plane_object):
    """Тест операции Delete."""
    temp_storage.add_airplane_info(sample_plane_object)
    deleted_count = temp_storage.delete_airplane_info(icao24="a1b2c3")

    assert deleted_count == 1
    assert temp_storage.get_airplane_info() == []


def test_speed_comparison():
    """Тест метода is_faster_than."""
    data_fast = VALID_PLANE_DATA.copy()
    data_fast[9] = 600.0

    data_slow = VALID_PLANE_DATA.copy()
    data_slow[9] = 400.0

    plane_fast = AirplaneInfo(data_fast)
    plane_slow = AirplaneInfo(data_slow)

    assert plane_fast.is_faster_than(plane_slow) is True
    assert plane_slow.is_faster_than(plane_fast) is False

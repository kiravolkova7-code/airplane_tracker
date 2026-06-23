import json
import os
import pytest
from src.airplane_info import AirplaneInfo, JsonAirplaneStorage

# Тестовые данные

VALID_PLANE_DATA = [
    "aabbcc",
    "ACME123",
    "Canada",
    None,
    None,
    -75.5,
    45.0,
    None,
    None,
    None
]

INCOMPLETE_PLANE_DATA = [
    None,
    "",
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None
]


def test_successful_initialization():
    """Тест: объект создается успешно и атрибуты заполнены верно."""
    plane = AirplaneInfo(VALID_PLANE_DATA)

    assert plane.icao24 == "aabbcc"
    assert plane.callsign == "ACME123"
    assert plane.country == "Canada"
    assert plane.longitude == -75.5
    assert plane.latitude == 45.0
    assert plane.altitude == 0.0
    assert plane.speed == 0.0


def test_initialization_with_incomplete_data():
    """Тест: объект создается с дефолтными значениями, если данных не хватает."""
    plane = AirplaneInfo(INCOMPLETE_PLANE_DATA)

    assert plane.callsign == ""

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

# Тесты для проверки работы с JSON файлом
# --- Фикстуры (Fixtures) ---

@pytest.fixture
def sample_plane_data():
    """Возвращает словарь с данными о самолете для тестов."""
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
    """Создает и возвращает объект AirplaneInfo из sample_plane_data."""
    return AirplaneInfo.from_dict(sample_plane_data)


@pytest.fixture
def temp_storage(tmp_path):
    """
    Создает экземпляр JsonAirplaneStorage с временным файлом.
    tmp_path - встроенная фикстура pytest, предоставляющая временный путь.
    """
    # Создаем временный файл для теста
    temp_file = tmp_path / "test_airplane_data.json"
    storage = JsonAirplaneStorage(filename=str(temp_file))
    return storage


# --- Тесты для методов сериализации/десериализации (AirplaneInfo) ---

def test_to_dict(sample_plane_object, sample_plane_data):
    """Проверяет, что метод to_dict() возвращает правильный словарь."""
    result_dict = sample_plane_object.to_dict()

    # Проверяем, что все ключи и значения совпадают с исходными данными
    assert result_dict == sample_plane_data


def test_from_dict(sample_plane_data):
    """Проверяет, что метод from_dict() корректно создает объект из словаря."""
    plane = AirplaneInfo.from_dict(sample_plane_data)

    # Проверяем, что атрибуты объекта совпадают со значениями из словаря
    assert plane.icao24 == sample_plane_data["icao24"]
    assert plane.callsign == sample_plane_data["callsign"]
    assert plane.speed == sample_plane_data["speed"]


# --- Тесты для класса JsonAirplaneStorage ---

def test_add_and_get_airplane(temp_storage, sample_plane_object):
    """Проверяет добавление самолета в хранилище и его последующее получение."""

    # Действие: добавляем самолет
    temp_storage.add_airplane_info(sample_plane_object)

    # Проверка 1: Получаем самолет по ICAO24 и проверяем его данные
    found_planes = temp_storage.get_airplane_info(icao24="a1b2c3")

    assert len(found_planes) == 1
    found_plane = found_planes[0]

    assert found_plane.icao24 == sample_plane_object.icao24
    assert found_plane.callsign == sample_plane_object.callsign


def test_get_by_multiple_criteria(temp_storage, sample_plane_object):
    """Проверяет поиск по нескольким критериям (страна и высота)."""

    # Подготовка: добавляем самолет
    temp_storage.add_airplane_info(sample_plane_object)

    # Действие: ищем по стране и высоте
    found_planes = temp_storage.get_airplane_info(country="United States", altitude=10000.0)

    # Проверка: должен быть найден ровно один самолет
    assert len(found_planes) == 1


def test_prevent_duplicates(temp_storage, sample_plane_object):
    """Проверяет, что в хранилище не добавляются дубликаты самолетов (по ICAO24)."""

    # Подготовка: добавляем один и тот же самолет дважды
    temp_storage.add_airplane_info(sample_plane_object)
    temp_storage.add_airplane_info(sample_plane_object)  # Повторное добавление

    # Проверка: в хранилище должен быть только один уникальный самолет
    found_planes = temp_storage.get_airplane_info()
    assert len(found_planes) == 1


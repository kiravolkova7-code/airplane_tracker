from src.airplane_info import AirplaneInfo

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

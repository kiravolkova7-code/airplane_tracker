from abc import ABC, abstractmethod
from src.airplane_info import AirplaneInfo
import requests


class ApiClient(ABC):
    """
    Базовый абстрактный класс для клиентов API.
    """

    @abstractmethod
    def get_data(self, endpoint: str, params: dict):
        """Абстрактный метод для выполнения GET-запроса."""
        pass


class NominatimApiClient(ApiClient):
    """
    Клиент для взаимодействия с API Nominatim.
    """
    BASE_URL = "https://nominatim.openstreetmap.org/"

    def __init__(self, user_agent="my_app/1.0"):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': user_agent})

    def get_data(self, endpoint: str, params: dict):
        response = self.session.get(self.BASE_URL + endpoint, params=params)
        response.raise_for_status()
        return response.json()

    def get_country_bounding_box(self, country_name):
        """
        Получает bounding box (границы) для указанной страны.
        """
        params = {
            'q': country_name,
            'format': 'json',
            'polygon_geojson': 0,
            'addressdetails': 1,
            'limit': 1,
        }
        data = self.get_data('search', params)
        if data and isinstance(data, list) and len(data) > 0:
            result = data[0]
            if 'boundingbox' in result and len(result['boundingbox']) == 4:
                # Nominatim возвращает строки — нужно привести к float
                south, north, west, east = result['boundingbox']
                return float(south), float(north), float(west), float(east)
        return None


class OpenSkyApiClient(ApiClient):
    """
    Клиент для взаимодействия с API OpenSky Network через прямые HTTP-запросы.
    Использует стандартную библиотеку 'requests'.
    """

    # Базовый URL-адрес API OpenSky
    BASE_URL = "https://opensky-network.org/api/states/all"

    def __init__(self):
        # Никаких сложных объектов создавать не нужно
        pass

    def get_data(self, endpoint: str, params: dict):
        pass

    def get_aircraft_in_area(self, lamin: float, lamax: float, lomin: float, lomax: float):
        """
        Получает список самолетов в заданной области через прямой HTTP-запрос.
        Параметры bbox передаются как query-параметры в URL.
        """
        try:
            print(f"[DEBUG] Запрос к {self.BASE_URL} с областью: {lamin}-{lamax}, {lomin}-{lomax}")

            # Формируем словарь параметров для запроса
            params = {
                'lamin': lamin,
                'lamax': lamax,
                'lomin': lomin,
                'lomax': lomax
            }

            # Выполняем GET-запрос
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()  # Проверка на ошибки HTTP (например, 404, 500)

            data = response.json()
            aircraft_list = []

            # Данные о самолетах находятся в ключе 'states'
            states = data.get('states', [])
            for s in states:
                try:
                    # Передаем ВНУТРЕННИЙ СПИСОК 's' напрямую в конструктор.
                    # Конструктор AirplaneInfo сам знает, как извлечь данные по индексам.
                    plane = AirplaneInfo(s)

                    # Устанавливаем страну регистрации.
                    # Поскольку 's' - это список, страна находится по индексу COUNTRY=2
                    if len(s) > 2 and s[2] is not None:
                        plane.country = str(s[2])
                    else:
                        plane.country = "N/A"

                    aircraft_list.append(plane)
                except ValueError as e:
                    print(f"[DEBUG] Пропущен самолет с некорректными данными: {e}")
                    continue

            return aircraft_list

        except requests.exceptions.RequestException as e:
            # Обрабатываем любые ошибки сети или HTTP
            print(f"[ERROR] Ошибка при запросе к OpenSky API: {e}")
            raise
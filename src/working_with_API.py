from abc import ABC, abstractmethod
import requests


class ApiClient(ABC):
    @abstractmethod
    def _make_request(self, url, params):
        pass

    def get_data(self, endpoint, query_params=None):
        if not hasattr(self, 'base_url'):
            raise ValueError("У класса должен быть атрибут base_url")
        url = f"{self.base_url}/{endpoint}"
        return self._make_request(url, query_params or {})


class NominatimApiClient(ApiClient):
    def __init__(self, user_agent):
        self.base_url = "https://nominatim.openstreetmap.org"
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': user_agent})

    def _make_request(self, url, params):
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_country_bounding_box(self, country_name):
        params = {
            'country': country_name,
            'format': 'json',
            'polygon_geojson': 0,
            'addressdetails': 1
        }
        data = self.get_data('search', params)
        if data and isinstance(data, list) and len(data) > 0:
            result = data[0]
            if 'boundingbox' in result and len(result['boundingbox']) == 4:
                return result['boundingbox']
        return None


class OpenSkyApiClient(ApiClient):
    def __init__(self):
        self.base_url = "https://opensky-network.org/api"
        self.session = requests.Session()

    def _make_request(self, url, params):
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_aircraft_in_area(self, lamin, lamax, lomin, lomax, time=0):
        endpoint = "states/all"
        params = {
            'lamin': lamin,
            'lamax': lamax,
            'lomin': lomin,
            'lomax': lomax,
            'time': time
        }
        return self.get_data(endpoint, params)

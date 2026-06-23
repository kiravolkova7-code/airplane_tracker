import json
from abc import ABC, abstractmethod
import os

# Константы для индексов данных в ответе API OpenSky
CALLSIGN = 1
COUNTRY = 2
LATITUDE = 6
LONGITUDE = 5
ALTITUDE = 3
SPEED = 9
ICAO24 = 0

class AirplaneInfo:
    """
    Класс для хранения информации о самолете.
    """
    def __init__(self, data):
        self.icao24 = "N/A"
        self.callsign = "N/A"
        self.country = "N/A"
        self.latitude = 0.0
        self.longitude = 0.0
        self.altitude = 0.0
        self.speed = 0.0

        try:
            self.icao24 = str(data[ICAO24]) if data[ICAO24] is not None else "N/A"
            self.callsign = str(data[CALLSIGN]).strip() if data[CALLSIGN] is not None else "N/A"
            self.country = str(data[COUNTRY]) if data[COUNTRY] is not None else "N/A"
            self.latitude = float(data[LATITUDE]) if data[LATITUDE] is not None else 0.0
            self.longitude = float(data[LONGITUDE]) if data[LONGITUDE] is not None else 0.0
            self.altitude = float(data[ALTITUDE]) if data[ALTITUDE] is not None else 0.0
            self.speed = float(data[SPEED]) if data[SPEED] is not None else 0.0
        except (IndexError, TypeError):
            pass

        self._validate()

    def _validate(self):
        """Приватный метод для проверки корректности данных."""
        if self.speed < 0:
            raise ValueError(f"Недопустимое значение скорости: {self.speed}.")
        if self.altitude < 0:
            raise ValueError(f"Недопустимое значение высоты: {self.altitude}.")

    def __eq__(self, other):
        """Сравнение на равенство по уникальному идентификатору ICAO24."""
        if not isinstance(other, AirplaneInfo):
            return False
        return self.icao24 == other.icao24

    def __str__(self):
        """Возвращает человекочитаемое представление объекта."""
        return (f"Самолет {self.callsign} (ICAO24: {self.icao24}) из {self.country}. "
                f"Текущие координаты: {self.latitude:.2f}, {self.longitude:.2f}. "
                f"Летит на высоте {self.altitude} м со скоростью {self.speed} узлов.")


    def to_dict(self):
        """Преобразует объект в словарь для сохранения в JSON."""
        return {
            "icao24": self.icao24,
            "callsign": self.callsign,
            "country": self.country,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude,
            "speed": self.speed,
        }

    @classmethod
    def from_dict(cls, data):
        """Создает объект AirplaneInfo из словаря."""
        list_data = [
            data.get("icao24", "N/A"),
            data.get("callsign", "N/A"),
            data.get("country", "N/A"),
            data.get("altitude", 0.0),
            None,
            data.get("longitude", 0.0),
            data.get("latitude", 0.0),
            None, None,
            data.get("speed", 0.0)
        ]
        return cls(list_data)


# Классы для работы с JSON-файлами
class AirplaneStorage(ABC):
    """
    Абстрактный базовый класс для хранилища информации о самолетах.
    """
    @abstractmethod
    def add_airplane_info(self, airplane_info):
        pass

    @abstractmethod
    def get_airplane_info(self, **criteria):
        pass

    @abstractmethod
    def delete_airplane_info(self, **criteria):
        pass

class JsonAirplaneStorage(AirplaneStorage):
    """
    Реализация хранилища AirplaneStorage, использующая JSON-файл.
    """
    def __init__(self, filename='data/airplane_info.json'):
        self.filename = filename

    def _load_data(self):
        """Загружает данные из JSON-файла."""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_data(self, data):
        """Сохраняет данные в JSON-файл."""
        os_dir = os.path.dirname(self.filename)
        if os_dir and not os.path.exists(os_dir):
            os.makedirs(os_dir)

        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_airplane_info(self, airplane_info):
        """Добавляет информацию о самолете в хранилище."""
        data = self._load_data()
        if not any(obj.get('icao24') == airplane_info.icao24 for obj in data):
            data.append(airplane_info.to_dict())
            self._save_data(data)

    def get_airplane_info(self, **criteria):
        """Получает список самолетов по указанным критериям."""
        data = self._load_data()
        results = []
        for obj in data:
            match = True
            for key, value in criteria.items():
                if obj.get(key) != value:
                    match = False
                    break
            if match:
                results.append(AirplaneInfo.from_dict(obj))
        return results

    def delete_airplane_info(self, **criteria):
        """Удаляет информацию о самолетах по указанным критериям."""
        data = self._load_data()
        original_len = len(data)
        filtered_data = [obj for obj in data if not all(obj.get(k) == v for k, v in criteria.items())]
        self._save_data(filtered_data)
        return original_len - len(filtered_data)

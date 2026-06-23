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
    Инициализируется данными из ответа API OpenSky (в виде списка).
    """
    def __init__(self, data):
        if not isinstance(data, list) or len(data) <= max(ICAO24, SPEED):
            self.icao24 = "N/A"
            self.callsign = "N/A"
            self.country = "N/A"
            self.latitude = 0.0
            self.longitude = 0.0
            self.altitude = 0.0
            self.speed = 0.0
            return

        self.icao24 = str(data[ICAO24]) if data[ICAO24] is not None else "N/A"
        self.callsign = str(data[CALLSIGN]).strip() if data[CALLSIGN] is not None else "N/A"
        self.country = str(data[COUNTRY]) if data[COUNTRY] is not None else "N/A"

        try:
            self.latitude = float(data[LATITUDE]) if data[LATITUDE] is not None else 0.0
            self.longitude = float(data[LONGITUDE]) if data[LONGITUDE] is not None else 0.0
            self.altitude = float(data[ALTITUDE]) if data[ALTITUDE] is not None else 0.0
            self.speed = float(data[SPEED]) if data[SPEED] is not None else 0.0
        except (TypeError, ValueError):
            self.latitude = 0.0
            self.longitude = 0.0
            self.altitude = 0.0
            self.speed = 0.0

        self._validate()

    def _validate(self):
        """Приватный метод для проверки корректности данных."""
        if self.speed < 0:
            raise ValueError(f"Недопустимое значение скорости: {self.speed}. Скорость не может быть отрицательной.")
        if self.altitude < 0:
            raise ValueError(f"Недопустимое значение высоты: {self.altitude}. Высота не может быть отрицательной.")

    # --- Методы сравнения ---
    def __eq__(self, other):
        """Сравнение на равенство по уникальному идентификатору ICAO24."""
        if not isinstance(other, AirplaneInfo):
            return False
        return self.icao24 == other.icao24

    def __lt__(self, other):
        """
        Сравнение "меньше чем".
        По умолчанию сравнивает по высоте полета.
        """
        if not isinstance(other, AirplaneInfo):
            return NotImplemented
        return self.altitude < other.altitude

    # --- Вспомогательные методы ---
    def __str__(self):
        """Возвращает человекочитаемое представление объекта."""
        return (f"Самолет {self.callsign} (ICAO24: {self.icao24}) из {self.country}. "
                f"Текущие координаты: {self.latitude:.2f}, {self.longitude:.2f}. "
                f"Летит на высоте {self.altitude} м со скоростью {self.speed} узлов.")

import requests
from src.airplane_info import AirplaneInfo
from src.working_with_API import OpenSkyApiClient, NominatimApiClient
# test_storage.py
import os
# Импортируем наш основной модуль с классами
# Если классы находятся в файле main.py, используйте: from main import JsonAirplaneStorage, AirplaneInfo
from src.airplane_info import JsonAirplaneStorage, AirplaneInfo

def main():
    # 1. Создаем экземпляр хранилища.
    # По умолчанию он будет использовать файл 'data/airplane_info.json'.
    storage = JsonAirplaneStorage()

    # 2. Создаем несколько объектов AirplaneInfo.
    # Данные передаются в виде списка, как это делает API OpenSky.
    plane1 = AirplaneInfo([
        "a1b2c3",  # ICAO24
        "AAL123",  # CALLSIGN
        "United States", # COUNTRY
        10000,     # ALTITUDE
        None,
        -97.0,     # LONGITUDE
        37.0,      # LATITUDE
        None, None,
        450.0      # SPEED
    ])

    plane2 = AirplaneInfo([
        "d4e5f6",
        "BAW456",
        "United Kingdom",
        12000,
        None,
        -0.1,      # LONGITUDE (Лондон)
        51.5,      # LATITUDE (Лондон)
        None, None,
        480.0
    ])

    plane3 = AirplaneInfo([
        "a1b2c3",  # Тот же ICAO24, что и у plane1
        "AAL123-NEW", # Другой позывной
        "United States",
        11000,
        None,
        -97.1,
        37.1,
        None, None,
        460.0
    ])

    print("--- Добавление данных в хранилище ---")
    # 3. Добавляем самолеты в хранилище.
    storage.add_airplane_info(plane1)
    storage.add_airplane_info(plane2)
    print("Добавлены два самолета.\n")

    # 4. Попытка добавить дубликат (по ICAO24).
    # Метод add_airplane_info проверяет на уникальность, поэтому plane3 не будет добавлен.
    print("Попытка добавить самолет с существующим ICAO24...")
    storage.add_airplane_info(plane3)
    print("Дубликат не добавлен.\n")

    print("--- Поиск данных в хранилище ---")
    # 5. Поиск по стране.
    us_planes = storage.get_airplane_info(country="United States")
    print(f"Найдено самолетов из США: {len(us_planes)}")
    for p in us_planes:
        print(f"  - {p.callsign} на высоте {p.altitude}м")

    # 6. Поиск по позывному (callsign).
    london_planes = storage.get_airplane_info(callsign="BAW456")
    print(f"\nНайдено самолетов с позывным BAW456: {len(london_planes)}")
    for p in london_planes:
        print(f"  - {p.country}, координаты: {p.latitude}, {p.longitude}")

    # 7. Поиск по нескольким критериям.
    high_planes = storage.get_airplane_info(country="United States", altitude=11000)
    print(f"\nНайдено самолетов из США на высоте 11000м: {len(high_planes)}")

    print("\n--- Удаление данных из хранилища ---")
    # 8. Удаление самолета по позывному.
    deleted_count = storage.delete_airplane_info(callsign="BAW456")
    print(f"Удалено записей по позывному BAW456: {deleted_count}")

    # 9. Проверяем, что самолет действительно удален.
    london_planes_after = storage.get_airplane_info(callsign="BAW456")
    print(f"Самолетов с позывным BAW456 после удаления: {len(london_planes_after)}")


if __name__ == "__main__":
    main()

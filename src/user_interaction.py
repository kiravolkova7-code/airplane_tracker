import os
from typing import List
from src.working_with_API import OpenSkyApiClient, NominatimApiClient
from src.airplane_info import AirplaneInfo, JsonAirplaneStorage
import time

def main():
    nominatim_client = NominatimApiClient(user_agent="my_app/1.0")
    opensky_client = OpenSkyApiClient()
    storage = JsonAirplaneStorage()

    # 1. Запрос страны и получение её границ
    country_name = input("Введите название страны (например, 'Russia'): ").strip()

    try:
        start_time = time.time()
        bbox = nominatim_client.get_country_bounding_box(country_name)
        elapsed_time = time.time() - start_time
        print(f"[DEBUG] Время запроса границ: {elapsed_time:.2f} сек.")
    except Exception as e:
        return

    if not bbox:
        print(f"[ERROR] Не удалось найти границы для страны: {country_name}")
        return
    else:
        lamin, lamax, lomin, lomax = bbox
        print(f"[DEBUG] Получены полные границы: {lamin}, {lamax}, {lomin}, {lomax})")
        print("Это очень большая область для запроса. Для быстрого ответа давайте уточним её.")

    # Запрос у пользователя более точной области
    try:
        # Предлагаем пользователю ввести координаты или использовать часть от полученных границ
        user_lamin = float(input(f"Введите минимальную широту (например, {lamin}): "))
        user_lamax = float(input(f"Введите максимальную широту (например, {lamax}): "))
        user_lomin = float(input(f"Введите минимальную долготу (например, {lomin}): "))
        user_lomax = float(input(f"Введите максимальную долготу (например, {lomax}): "))

        # Проверка корректности введенных координат
        if not (user_lamin < user_lamax and user_lomin < user_lomax):
            print("[ERROR] Ошибка: минимальная координата должна быть меньше максимальной.")
            return

        # Используем введенные пользователем координаты для финального запроса
        lamin, lamax, lomin, lomax = user_lamin, user_lamax, user_lomin, user_lomax

    except ValueError:
        print("[ERROR] Ошибка: введите числовые значения для координат.")
        return

    # 2. Запрос количества самолетов (N)
    try:
        n = int(input("Введите количество самолетов для топа по высоте: ").strip())
        if n <= 0:
            print("[ERROR] Количество должно быть положительным числом.")
            return
    except ValueError:
        print("[ERROR] Ошибка: введите целое число.")
        return

    # 3. Получение данных о самолетах в уточненной области
    print(f"[DEBUG] Начало запроса данных у OpenSky для области: {lamin}-{lamax}, {lomin}-{lomax}...")
    try:
        start_time = time.time()
        aircraft_list = opensky_client.get_aircraft_in_area(lamin, lamax, lomin, lomax)
        elapsed_time = time.time() - start_time
        print(f"[DEBUG] Время запроса к OpenSky API: {elapsed_time:.2f} сек.")
    except Exception as e:
        # Этот блок сработает только если запрос вернет ошибку HTTP
        print(f"[ERROR] Ошибка при запросе к OpenSky API: {e}")
        return

    # Обработка результата
    if not aircraft_list:
        print("[INFO] В указанной области самолеты не обнаружены.")
        return

    # 4. Вывод результатов (теперь это будет работать быстро)
    print(f"\n[INFO] Успешно получено {len(aircraft_list)} самолетов.")

    # Сохранение данных в хранилище (может занять время при большом N)
    save_count = 0
    for aircraft in aircraft_list:
        storage.add_airplane_info(aircraft)
        save_count += 1
    print(f"[INFO] Сохранено в файл: {save_count} записей.")

    # 5. Вывод топ-N самолетов по высоте
    top_n_aircraft = sorted(aircraft_list, key=lambda a: a.altitude, reverse=True)[:n]
    print(f"\nТоп-{n} самолетов по высоте полета:")
    for i, aircraft in enumerate(top_n_aircraft, 1):
        print(f"{i}. {aircraft}")

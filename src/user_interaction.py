from src.working_with_API import OpenSkyApiClient, NominatimApiClient
from src.airplane_info import JsonAirplaneStorage
import time
import requests


def main():
    """
    Главная функция программы. Выполняет все шаги: от запроса страны до вывода топ-N самолетов.
    """
    # 1. Инициализация клиентов и хранилища
    nominatim_client = NominatimApiClient(user_agent="my_app/1.0")
    opensky_client = OpenSkyApiClient()
    storage = JsonAirplaneStorage()

    # 2.1 Запрос стран регистрации для фильтрации
    registration_filter = input(
        "Введите страны регистрации для фильтрации (через пробел, Enter — без фильтра): "
    ).strip()

    filter_countries = [c.strip().lower() for c in registration_filter.split()] if registration_filter else []

    # 2.2 Запрос страны и получение её границ
    country_name = input("Введите название страны (например, 'Russia'): ").strip()
    try:
        start_time = time.time()
        bbox = nominatim_client.get_country_bounding_box(country_name)
        elapsed_time = time.time() - start_time
        print(f"[DEBUG] Время запроса границ: {elapsed_time:.2f} сек.")
    except Exception as e:
        print(f"[ERROR] Ошибка при запросе границ страны: {e}")
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
        user_lamin = float(input(f"Введите минимальную широту (например, {lamin}): "))
        user_lamax = float(input(f"Введите максимальную широту (например, {lamax}): "))
        user_lomin = float(input(f"Введите минимальную долготу (например, {lomin}): "))
        user_lomax = float(input(f"Введите максимальную долготу (например, {lomax}): "))

        # Проверка корректности введенных координат
        if not (user_lamin < user_lamax and user_lomin < user_lomax):
            print("[ERROR] Ошибка: минимальная координата должна быть меньше максимальной.")
            return
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
        params = {
            "lamin": lamin,
            "lamax": lamax,
            "lomin": lomin,
            "lomax": lomax
        }
        aircraft_list = opensky_client.get_aircraft_in_area(**params)
    except requests.exceptions.RequestException as e:  # Уточняем тип ошибки
        print(f"[ERROR] Сбой сетевого соединения или ошибка HTTP: {e}")
        return
    except Exception as e:
        print(f"[ERROR] Неизвестная ошибка при запросе к API: {e}")
        return

    # --- ОБРАБОТКА РЕЗУЛЬТАТА ---

    # Сохраняем исходное количество ДО любой фильтрации
    original_count = len(aircraft_list)

    # 1. Дебаг-вывод: Проверяем первые 20 самолетов, чтобы увидеть реальные данные
    print("[DEBUG] Точная проверка значений поля 'country' у первых 20 самолетов:")
    for i, plane in enumerate(aircraft_list[:20], 1):
        country_str = str(plane.country)  # На случай, если там None
        length = len(country_str)
        print(
            f"  [{i}] Длина='{length}', Значение через repr()=repr({country_str!r}), Значение через str()='{country_str}'")

    print(
         f"\n[DEBUG] Итого получено от API: {original_count} самолетов."
    )

    # Если список пустой после запроса, выходим
    if original_count == 0:
        print("\n[INFO] В указанной области самолеты не обнаружены.")
        return

    # 2. Применение фильтрации по стране регистрации (ПОСЛЕ получения данных!)
    if filter_countries:
        # Используем .strip(), чтобы убрать лишние пробелы, которые могут быть в данных
        filtered_list = [
            aircraft for aircraft in aircraft_list
            if str(aircraft.country).lower().strip() in filter_countries
        ]

        # Заменяем основной список на отфильтрованный
        aircraft_list = filtered_list

        # Проверяем результат фильтрации
        if not aircraft_list:
            print("\n[INFO] Самолёты с указанными странами регистрации не найдены.")
            return
        else:
            print(
                f"\n[INFO] Отфильтровано по стране. Из {original_count} найденных самолётов осталось {len(aircraft_list)}."
            )

    # 3. Сохранение данных в хранилище
    save_count = 0
    for aircraft in aircraft_list:
        storage.add_airplane_info(aircraft)
        save_count += 1
    print(f"\n[INFO] Сохранено в файл: {save_count} записей.")

    # 4. Вывод топ-N самолетов по высоте
    top_n_aircraft = sorted(aircraft_list, key=lambda a: a.altitude, reverse=True)[:n]

    print(f"\nТоп-{n} самолетов по высоте полета:")
    for i, aircraft in enumerate(top_n_aircraft, 1):
        print(f"{i}. {aircraft}")

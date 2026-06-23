from src.working_with_API import *

if __name__ == "__main__":
    # Задаем имя страны
    country = "Canada"

    # Создаем клиент для OSM и получаем координаты
    osm_client = NominatimApiClient(user_agent="my-university-coursework/1.0")
    bbox = osm_client.get_country_bounding_box(country)

    if bbox is None:
        print(f"Не удалось найти страну '{country}'")
    else:
        south, north, west, east = map(float, bbox)
        print(f"Координаты {country}: Юг={south}, Север={north}, Запад={west}, Восток={east}")

        # Создаем клиент для OpenSky и запрашиваем данные о самолетах
        sky_client = OpenSkyApiClient()
        aircraft_data = sky_client.get_aircraft_in_area(south, north, west, east)

        # Обрабатываем полученные данные
        states = aircraft_data.get('states', [])
        print(f"\nНайдено самолетов в воздушном пространстве {country}: {len(states)}")
        for state in states[:5]:  # Покажем первые 5 для примера
            callsign = state[1].strip() if state[1] else "Нет данных"
            print(f"- Борт: {callsign}, Высота: {state[7]} м, Скорость: {state[9]} узлов")

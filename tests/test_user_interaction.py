import pytest
from unittest.mock import patch, MagicMock, call
from src.user_interaction import main

import pytest
from unittest.mock import patch, MagicMock


# --- Тест 2: Обработка ошибки - страна не найдена ---
@patch('builtins.input')
@patch('src.working_with_API.NominatimApiClient')
def test_main_country_not_found(mock_nominatim_class, mock_input, capsys):
    # Настройка ввода и ответа API (пустой bbox)
    mock_input.side_effect = ['UnknownCountry']

    mock_nominatim_client = mock_nominatim_class.return_value
    mock_nominatim_client.get_country_bounding_box.return_value = None

    # Запуск функции main()
    main()

    # Проверка вывода сообщения об ошибке
    captured = capsys.readouterr()
    output = captured.out

    assert "[ERROR] Не удалось найти границы для страны: UnknownCountry" in output


# --- Тест 3: Обработка ошибки - некорректные координаты ---
@patch('builtins.input')
def test_main_invalid_coordinates(mock_input, capsys):
    # Настройка ввода: вводим max_lat меньше min_lat, что вызовет ошибку в коде.
    # Нужно предоставить все 6 значений, чтобы дойти до проверки if.
    mock_input.side_effect = [
        'Russia',
        '60.0',  # user_lamin
        '50.0',  # user_lamax (меньше min!)
        '30.0',  # user_lomin
        '40.0',  # user_lomax
        '2'  # n
    ]

    # Запуск функции main()
    main()

    # Проверка вывода сообщения об ошибке координат
    captured = capsys.readouterr()
    output = captured.out

    assert "[ERROR] Ошибка: минимальная координата должна быть меньше максимальной." in output

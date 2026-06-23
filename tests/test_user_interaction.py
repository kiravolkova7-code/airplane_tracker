from src.user_interaction import main
from unittest.mock import patch


@patch('builtins.input')
@patch('src.working_with_API.NominatimApiClient')
def test_main_country_not_found(mock_nominatim_class, mock_input, capsys):
    mock_input.side_effect = ['UnknownCountry']

    mock_nominatim_client = mock_nominatim_class.return_value
    mock_nominatim_client.get_country_bounding_box.return_value = None

    main()

    captured = capsys.readouterr()
    output = captured.out

    assert "[ERROR] Не удалось найти границы для страны: UnknownCountry" in output


@patch('builtins.input')
def test_main_invalid_coordinates(mock_input, capsys):
    mock_input.side_effect = [
        'Russia',
        '60.0',
        '50.0',
        '30.0',
        '40.0',
        '2'
    ]

    main()

    captured = capsys.readouterr()
    output = captured.out

    assert "[ERROR] Ошибка: минимальная координата должна быть меньше максимальной." in output

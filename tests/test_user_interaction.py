from src.user_interaction import main
from unittest.mock import patch


@patch('builtins.input')
@patch('src.user_interaction.NominatimApiClient')
def test_main_country_not_found(mock_nominatim_class, mock_input, capsys):
    mock_input.side_effect = ['UnknownCountry']

    mock_nominatim_client = mock_nominatim_class.return_value
    mock_nominatim_client.get_country_bounding_box.return_value = None

    main()

    captured = capsys.readouterr()
    output = captured.out

    assert "[ERROR] Не удалось найти границы для страны: UnknownCountry" in output


@patch('builtins.input')
@patch('src.user_interaction.NominatimApiClient')
def test_main_invalid_coordinates(mock_nominatim_class, mock_input, capsys):
    mock_input.side_effect = ['Russia', '60.0', '50.0', '30.0', '40.0', '2']
    mock_nominatim_class.return_value.get_country_bounding_box.return_value = (
        41.0,
        82.0,
        19.0,
        180.0
    )

    main()
    output = capsys.readouterr().out
    assert "[ERROR] Ошибка: минимальная координата должна быть меньше максимальной." in output


@patch('builtins.input')
@patch('src.user_interaction.OpenSkyApiClient')
@patch('src.user_interaction.NominatimApiClient')
def test_filter_by_registration_country(mock_nominatim_class, mock_opensky_class, mock_input, capsys):
    mock_input.side_effect = [
        'Spain', '36.0', '44.0', '-10.0', '5.0', '10', 'France'
    ]
    mock_nominatim_class.return_value.get_country_bounding_box.return_value = (
        36.0, 44.0, -10.0, 5.0
    )

    plane_fr = MagicMock()
    plane_fr.country = 'France'
    plane_fr.altitude = 10000
    plane_us = MagicMock()
    plane_us.country = 'United States'
    plane_us.altitude = 9000

    mock_opensky_class.return_value.get_aircraft_in_area.return_value = [plane_fr, plane_us]

    main()
    output = capsys.readouterr().out
    assert 'France' in output
    assert 'United States' not in output
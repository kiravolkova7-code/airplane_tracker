from unittest.mock import patch
from src.user_interaction import main


@patch('src.user_interaction.input', side_effect=["", "Testland", "50", "60", "30", "40", "1"])
@patch('src.user_interaction.NominatimApiClient')
@patch('src.user_interaction.OpenSkyApiClient')
def test_main_network_error(mock_opensky_class, mock_nominatim_class, mock_input, capsys):
    """
    Тест обработки исключения при запросе к API.
    """
    mock_nominatim_instance = mock_nominatim_class.return_value
    mock_nominatim_instance.get_country_bounding_box.return_value = (50.0, 60.0, 30.0, 40.0)

    mock_opensky_instance = mock_opensky_class.return_value
    mock_opensky_instance.get_aircraft_in_area.side_effect = Exception("Bad Gateway")

    main()

    captured = capsys.readouterr().out
    mock_opensky_instance.get_aircraft_in_area.assert_called_once_with(lamin=50.0, lamax=60.0, lomin=30.0, lomax=40.0)
    assert "[ERROR] Неизвестная ошибка при запросе к API: Bad Gateway" in captured

# main.py

from src.user_interaction import main
from src.working_with_API import OpenSkyApiClient, NominatimApiClient
from src.airplane_info import AirplaneInfo, JsonAirplaneStorage
import time

if __name__ == "__main__":
    main()
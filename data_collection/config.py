from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")

LATITUDE = 27.7172
LONGITUDE = 85.3240

BASE_URL = "https://api.openweathermap.org/data/2.5/air_pollution"
import sys
import os

# Add the project root to Python's search path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from datetime import datetime


from api_client import get_air_quality
from save_csv import save_data
import requests
from database.database import create_table, insert_data


def fetch():

    create_table()

    data = get_air_quality()

    if data is None:
        return

    air = data["list"][0]

    components = air["components"]

    row = {

        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        "aqi": air["main"]["aqi"],

        "pm2_5": components["pm2_5"],

        "pm10": components["pm10"],

        "co": components["co"],

        "no2": components["no2"],

        "o3": components["o3"],

        "so2": components["so2"]

    }

    insert_data(row)


if __name__ == "__main__":
    fetch()
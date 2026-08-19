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
from aqi_calculation import calculate_aqi


def fetch():

    create_table()

    data = get_air_quality()

    if data is None:
        return

    air = data["list"][0]

    components = air["components"]

    pm2_5 = components["pm2_5"]
    pm10 = components["pm10"]
    co = components["co"]
    no2 = components["no2"]
    o3 = components["o3"]
    so2 = components["so2"]

    calc_aqi, primary = calculate_aqi(pm2_5, pm10, co, no2, o3, so2)

    row = {

        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        "aqi": air["main"]["aqi"],

        "pm2_5": pm2_5,

        "pm10": pm10,

        "co": co,

        "no2": no2,

        "o3": o3,

        "so2": so2,

        "calculated_aqi": calc_aqi,

        "primary_pollutant": primary

    }

    insert_data(row)


if __name__ == "__main__":
    fetch()
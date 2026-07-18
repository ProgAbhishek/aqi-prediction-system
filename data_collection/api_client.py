import requests
from config import API_KEY, LATITUDE, LONGITUDE, BASE_URL


def get_air_quality():

    url = (
        f"{BASE_URL}"
        f"?lat={LATITUDE}"
        f"&lon={LONGITUDE}"
        f"&appid={API_KEY}"
    )

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()

    print("Error:", response.status_code)
    return None
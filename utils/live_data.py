import requests
from datetime import datetime
from zoneinfo import ZoneInfo


def get_live_time(timezone_name="America/New_York"):
    return datetime.now(ZoneInfo(timezone_name))


def get_live_weather(latitude=33.7537, longitude=-84.3863):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}&longitude={longitude}"
        "&current=temperature_2m,precipitation,weather_code,cloud_cover"
        "&timezone=auto"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()["current"]

        precipitation = data.get("precipitation", 0)
        cloud_cover = data.get("cloud_cover", 0)

        if precipitation and precipitation > 0:
            weather_label = "rainy"
        elif cloud_cover is not None and cloud_cover >= 60:
            weather_label = "cloudy"
        else:
            weather_label = "sunny"

        return {
            "weather_label": weather_label,
            "temperature": data.get("temperature_2m"),
            "precipitation": precipitation,
            "cloud_cover": cloud_cover,
            "weather_code": data.get("weather_code"),
            "success": True,
        }
    except Exception:
        return {
            "weather_label": "sunny",
            "temperature": None,
            "precipitation": None,
            "cloud_cover": None,
            "weather_code": None,
            "success": False,
        }
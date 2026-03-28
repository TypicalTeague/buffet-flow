from datetime import datetime
from zoneinfo import ZoneInfo

import requests

from config import SERVICE_WINDOWS


def get_live_time(timezone_name: str = "America/New_York") -> datetime:
    return datetime.now(ZoneInfo(timezone_name))


def get_live_weather(latitude: float = 33.7537, longitude: float = -84.3863) -> dict:
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


def derive_meal_period_and_window(current_hour: int) -> tuple[str, int, str]:
    if 7 <= current_hour <= 10:
        return "breakfast", 1, "Opening Window"

    if 11 <= current_hour <= 14:
        if current_hour <= 12:
            return "lunch", 1, "Opening Window"
        if current_hour == 13:
            return "lunch", 2, "Peak Service"
        return "lunch", 3, "Closing Window"

    if 17 <= current_hour <= 20:
        if current_hour <= 18:
            return "dinner", 1, "Opening Window"
        if current_hour == 19:
            return "dinner", 2, "Peak Service"
        return "dinner", 3, "Closing Window"

    return "lunch", 2, SERVICE_WINDOWS[2]
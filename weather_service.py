import requests

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def get_current_weather(latitude: float, longitude: float):

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "rain,"
            "wind_speed_10m,"
            "surface_pressure"
        ),
        "hourly": "precipitation,rain",
        "past_hours": 168,
        "forecast_hours": 1,
        "timezone": "auto"
    }

    response = requests.get(
        OPEN_METEO_URL,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    current = data.get("current", {})
    hourly = data.get("hourly", {})

    precipitation = hourly.get("precipitation", [])

    precipitation = [
        x for x in precipitation
        if x is not None
    ]

    def rainfall(hours):
        if not precipitation:
            return 0.0

        return round(sum(precipitation[-hours:]), 2)

    return {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": data.get("timezone"),

        "temperature_c": current.get("temperature_2m"),
        "humidity_percent": current.get("relative_humidity_2m"),
        "precipitation_mm": current.get("precipitation"),
        "rain_mm": current.get("rain"),
        "wind_speed_kmh": current.get("wind_speed_10m"),
        "surface_pressure_hpa": current.get("surface_pressure"),

        "rain_1h": rainfall(1),
        "rain_3h": rainfall(3),
        "rain_6h": rainfall(6),
        "rain_12h": rainfall(12),
        "rain_24h": rainfall(24),
        "rain_3d": rainfall(72),
        "rain_7d": rainfall(168),

        "timestamp": current.get("time")
    }

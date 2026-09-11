import math
import requests


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def get_terrain(latitude: float, longitude: float):

    points = [
        (latitude, longitude),
        (latitude + 0.01, longitude),
        (latitude - 0.01, longitude),
        (latitude, longitude + 0.01),
        (latitude, longitude - 0.01),
    ]

    latitudes = ",".join(str(p[0]) for p in points)
    longitudes = ",".join(str(p[1]) for p in points)

    response = requests.get(
        OPEN_METEO_URL,
        params={
            "latitude": latitudes,
            "longitude": longitudes,
            "forecast_days": 1,
            "timezone": "auto"
        },
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    # Multiple coordinates return a list
    if isinstance(data, list):
        elevations = [
            float(item.get("elevation", 0))
            for item in data
        ]
    else:
        elevations = [
            float(data.get("elevation", 0))
        ]

    if len(elevations) < 5:
        return {
            "elevation": elevations[0] if elevations else 0.0,
            "slope": 0.0
        }

    center = elevations[0]

    north = elevations[1]
    south = elevations[2]
    east = elevations[3]
    west = elevations[4]

    # Approximate distance between points
    distance_m = 1110.0

    north_south_difference = abs(north - south)
    east_west_difference = abs(east - west)

    slope_ns = math.degrees(
        math.atan(
            north_south_difference /
            (distance_m * 2)
        )
    )

    slope_ew = math.degrees(
        math.atan(
            east_west_difference /
            (distance_m * 2)
        )
    )

    slope = max(slope_ns, slope_ew)

    return {
        "elevation": round(center, 2),
        "slope": round(slope, 2)
    }

import math
import requests


OVERPASS_URL = "https://overpass-api.de/api/interpreter"

HEADERS = {
    "User-Agent": "ResQRoute/1.0"
}


def haversine_distance(lat1, lon1, lat2, lon2):

    R = 6371.0

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return R * c


def get_distance_to_river(latitude, longitude):

    query = f"""
    [out:json][timeout:20];

    (
      way(around:10000,{latitude},{longitude})["waterway"="river"];
      way(around:10000,{latitude},{longitude})["waterway"="stream"];
      way(around:10000,{latitude},{longitude})["waterway"="canal"];
    );

    out geom;
    """

    response = requests.post(
        OVERPASS_URL,
        data={"data": query},
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    nearest_distance = None

    for element in data.get("elements", []):

        geometry = element.get("geometry", [])

        for point in geometry:

            point_lat = point.get("lat")
            point_lon = point.get("lon")

            if point_lat is None or point_lon is None:
                continue

            distance = haversine_distance(
                latitude,
                longitude,
                point_lat,
                point_lon
            )

            if (
                nearest_distance is None
                or distance < nearest_distance
            ):
                nearest_distance = distance

    if nearest_distance is None:
        return 10.0

    return round(nearest_distance, 3)

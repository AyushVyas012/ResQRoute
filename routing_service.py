import requests

OSRM_URL = "https://router.project-osrm.org/route/v1/driving"


def get_routes(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float
):
    coordinates = (
        f"{start_lon},{start_lat};"
        f"{end_lon},{end_lat}"
    )

    params = {
        "alternatives": "true",
        "steps": "true",
        "geometries": "geojson",
        "overview": "full"
    }

    response = requests.get(
        f"{OSRM_URL}/{coordinates}",
        params=params,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    if data.get("code") != "Ok":
        raise ValueError("No route found")

    routes = []

    for index, route in enumerate(data.get("routes", [])):

        routes.append({
            "route_id": index + 1,
            "distance_km": round(route["distance"] / 1000, 2),
            "duration_minutes": round(route["duration"] / 60, 1),
            "geometry": route["geometry"],
            "steps": route.get("legs", [])
        })

    return routes
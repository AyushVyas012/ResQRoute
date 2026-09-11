import json
import math
import urllib.parse
import urllib.request


OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

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


def _search_overpass(
    latitude,
    longitude,
    amenity,
    radius_m=5000
):
    """
    Search one emergency-service category at a time.

    This is intentionally smaller than the previous
    combined police + hospital + fire query so that
    one slow category does not break the entire SOS flow.
    """

    query = f"""
    [out:json][timeout:12];

    (
        node["amenity"="{amenity}"]
        (around:{radius_m},{latitude},{longitude});

        way["amenity"="{amenity}"]
        (around:{radius_m},{latitude},{longitude});

        relation["amenity"="{amenity}"]
        (around:{radius_m},{latitude},{longitude});
    );

    out center tags;
    """

    encoded = urllib.parse.urlencode({
        "data": query
    }).encode()

    last_error = None

    for base_url in OVERPASS_URLS:

        try:
            request = urllib.request.Request(
                base_url,
                data=encoded,
                headers={
                    "User-Agent": "ResQRoute/1.0"
                },
                method="POST"
            )

            with urllib.request.urlopen(
                request,
                timeout=18
            ) as response:

                raw_data = response.read().decode()

            data = json.loads(raw_data)

            results = []

            for element in data.get("elements", []):

                tags = element.get("tags", {})

                lat = element.get("lat")
                lon = element.get("lon")

                if lat is None or lon is None:

                    center = element.get(
                        "center",
                        {}
                    )

                    lat = center.get("lat")
                    lon = center.get("lon")

                if lat is None or lon is None:
                    continue

                lat = float(lat)
                lon = float(lon)

                distance = haversine_km(
                    latitude,
                    longitude,
                    lat,
                    lon
                )

                if amenity == "police":

                    service_type = "police"
                    label = "Police Station"

                elif amenity == "hospital":

                    service_type = "hospital"
                    label = "Hospital"

                elif amenity == "fire_station":

                    service_type = "fire"
                    label = "Fire Station"

                else:
                    continue

                results.append({
                    "type": service_type,
                    "label": label,
                    "name": (
                        tags.get("name")
                        or label
                    ),
                    "latitude": lat,
                    "longitude": lon,
                    "distance_km": round(
                        distance,
                        2
                    ),
                    "phone": (
                        tags.get("phone")
                        or tags.get(
                            "contact:phone"
                        )
                    )
                })

            results.sort(
                key=lambda item:
                item["distance_km"]
            )

            return results

        except Exception as error:

            last_error = error

            continue

    print(
        f"Overpass search failed for "
        f"{amenity}: {last_error}"
    )

    return []


def search_nearby_emergency_services(
    latitude,
    longitude,
    radius_m=5000
):

    all_services = []

    # Search independently.
    # If one category fails, the others can still work.

    for amenity in [
        "hospital",
        "police",
        "fire_station"
    ]:

        services = _search_overpass(
            latitude,
            longitude,
            amenity,
            radius_m
        )

        all_services.extend(services)

    all_services.sort(
        key=lambda item:
        item["distance_km"]
    )

    return all_services


def get_nearest_services(
    latitude,
    longitude
):

    services = search_nearby_emergency_services(
        latitude,
        longitude,
        radius_m=5000
    )

    nearest = {
        "police": None,
        "hospital": None,
        "fire": None
    }

    for service in services:

        service_type = service["type"]

        if nearest[service_type] is None:

            nearest[service_type] = service

    return {
        "police": nearest["police"],
        "hospital": nearest["hospital"],
        "fire": nearest["fire"],
        "all_services": services[:15]
    }
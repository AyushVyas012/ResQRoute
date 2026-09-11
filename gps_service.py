"""
GPS Service for ResQRoute

Handles:
- GPS coordinate validation
- Current location storage
- Current location retrieval
- Distance calculations
"""

import math
from typing import Optional


_current_location = None


def validate_coordinates(
    latitude: float,
    longitude: float
) -> bool:

    if latitude < -90 or latitude > 90:
        return False

    if longitude < -180 or longitude > 180:
        return False

    return True


def update_location(
    latitude: float,
    longitude: float
) -> dict:

    global _current_location

    if not validate_coordinates(
        latitude,
        longitude
    ):
        raise ValueError(
            "Invalid latitude or longitude"
        )

    _current_location = {
        "latitude": round(
            float(latitude),
            6
        ),
        "longitude": round(
            float(longitude),
            6
        ),
    }

    return _current_location


def get_current_location() -> Optional[dict]:

    return _current_location


# Compatibility function
# Existing location.py may use get_location()
def get_location() -> Optional[dict]:

    return get_current_location()


def clear_location():

    global _current_location

    _current_location = None


def calculate_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:

    R = 6371.0

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)

    delta_lat = math.radians(
        lat2 - lat1
    )

    delta_lon = math.radians(
        lon2 - lon1
    )

    a = (
        math.sin(delta_lat / 2) ** 2
        +
        math.cos(lat1_rad)
        * math.cos(lat2_rad)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return round(
        R * c,
        3
    )


def distance_from_current_location(
    latitude: float,
    longitude: float
) -> Optional[float]:

    if _current_location is None:
        return None

    return calculate_distance(
        _current_location["latitude"],
        _current_location["longitude"],
        latitude,
        longitude
    )


def is_location_available() -> bool:

    return _current_location is not None
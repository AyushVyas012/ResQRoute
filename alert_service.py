from datetime import datetime


def create_accident_alert(
    latitude: float,
    longitude: float
):

    return {
        "type": "ACCIDENT",
        "severity": "CRITICAL",
        "message": (
            "Accident detected/reported. "
            "Emergency services are being located."
        ),
        "latitude": latitude,
        "longitude": longitude,
        "timestamp": datetime.utcnow().isoformat()
    }


def create_emergency_alert(
    message: str,
    latitude: float,
    longitude: float
):

    return {
        "type": "EMERGENCY",
        "severity": "CRITICAL",
        "message": message,
        "latitude": latitude,
        "longitude": longitude,
        "timestamp": datetime.utcnow().isoformat()
    }
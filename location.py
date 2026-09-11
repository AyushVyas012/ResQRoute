from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.gps_service import get_location
from app.services.weather_service import get_current_weather


router = APIRouter(
    prefix="/location",
    tags=["Location"]
)


class LocationRequest(BaseModel):
    latitude: float
    longitude: float


# --------------------------------------------------
# Update GPS Location
# --------------------------------------------------

@router.post("/update")
def update_location(location: LocationRequest):

    try:
        data = get_location(
            location.latitude,
            location.longitude
        )

        return {
            "success": True,
            "message": "GPS location received",
            "data": data
        }

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# --------------------------------------------------
# Get Weather Using GPS Location
# --------------------------------------------------

@router.post("/weather")
def location_weather(location: LocationRequest):

    try:
        weather = get_current_weather(
            location.latitude,
            location.longitude
        )

        return {
            "success": True,
            "location": {
                "latitude": location.latitude,
                "longitude": location.longitude
            },
            "weather": weather
        }

    except Exception as e:

        raise HTTPException(
            status_code=502,
            detail=f"Unable to fetch weather: {str(e)}"
        )
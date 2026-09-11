from fastapi import APIRouter, HTTPException, Query

from app.services.weather_service import get_current_weather


router = APIRouter(
    prefix="/weather",
    tags=["Weather"]
)


@router.get("/current")
def current_weather(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180)
):
    try:
        weather = get_current_weather(latitude, longitude)

        return {
            "success": True,
            "data": weather
        }

    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to fetch live weather: {str(e)}"
        )
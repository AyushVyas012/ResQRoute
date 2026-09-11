from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.ml.landslide_model import predict_landslide_risk
from app.services.weather_service import get_current_weather
from app.services.terrain_service import get_terrain
from app.services.river_service import get_distance_to_river


router = APIRouter(
    prefix="/landslide",
    tags=["Landslide Risk"]
)


class LandslideRequest(BaseModel):
    latitude: float
    longitude: float


@router.post("/predict")
def predict_landslide(request: LandslideRequest):

    try:
        weather = get_current_weather(
            request.latitude,
            request.longitude
        )

        terrain = get_terrain(
            request.latitude,
            request.longitude
        )

        distance_to_river = get_distance_to_river(
            request.latitude,
            request.longitude
        )

        features = {
            "latitude": request.latitude,
            "longitude": request.longitude,

            "rain_1h": weather["rain_1h"],
            "rain_6h": weather["rain_6h"],
            "rain_24h": weather["rain_24h"],
            "rain_3d": weather["rain_3d"],

            "temperature": weather["temperature_c"],
            "humidity": weather["humidity_percent"],
            "wind_speed": weather["wind_speed_kmh"],

            "elevation": terrain["elevation"],
            "slope": terrain["slope"],

            "soil_moisture": 0.5,

            "distance_to_river": distance_to_river
        }

        result = predict_landslide_risk(features)

        return {
            "success": True,
            "location": {
                "latitude": request.latitude,
                "longitude": request.longitude
            },
            "weather": weather,
            "terrain": terrain,
            "distance_to_river_km": distance_to_river,
            "landslide_risk": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Landslide prediction failed: {str(e)}"
        )

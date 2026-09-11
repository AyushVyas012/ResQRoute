from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.ml.flood_model import predict_flood_risk
from app.services.weather_service import get_current_weather
from app.services.terrain_service import get_terrain
from app.services.river_service import get_distance_to_river


router = APIRouter(
    prefix="/flood",
    tags=["Flood Risk"]
)


class FloodLocationRequest(BaseModel):
    latitude: float
    longitude: float


@router.post("/predict")
def predict_flood(request: FloodLocationRequest):

    try:

        # 1. Live weather
        weather = get_current_weather(
            request.latitude,
            request.longitude
        )

        # 2. Real terrain
        terrain = get_terrain(
            request.latitude,
            request.longitude
        )

        # 3. Real distance to nearest waterway
        distance_to_river = get_distance_to_river(
            request.latitude,
            request.longitude
        )

        # 4. Prepare ML features
        features = {
            "latitude": request.latitude,
            "longitude": request.longitude,

            "rain_1h": weather["rain_1h"],
            "rain_3h": weather["rain_3h"],
            "rain_6h": weather["rain_6h"],
            "rain_12h": weather["rain_12h"],
            "rain_24h": weather["rain_24h"],
            "rain_3d": weather["rain_3d"],
            "rain_7d": weather["rain_7d"],

            "temperature": weather["temperature_c"],
            "humidity": weather["humidity_percent"],
            "wind_speed": weather["wind_speed_kmh"],
            "pressure": weather["surface_pressure_hpa"],

            "elevation": terrain["elevation"],
            "slope": terrain["slope"],

            "distance_to_river": distance_to_river
        }

        # 5. ML prediction
        result = predict_flood_risk(features)

        return {
            "success": True,

            "location": {
                "latitude": request.latitude,
                "longitude": request.longitude
            },

            "weather": weather,

            "terrain": terrain,

            "distance_to_river_km": distance_to_river,

            "flood_risk": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=502,
            detail=f"Flood prediction failed: {str(e)}"
        )

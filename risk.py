from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests

router = APIRouter(
    prefix="/risk",
    tags=["Risk Analysis"]
)


class RiskRequest(BaseModel):
    latitude: float
    longitude: float


@router.post("/analyze")
def analyze_risk(request: RiskRequest):

    try:
        flood_response = requests.post(
            "http://127.0.0.1:8000/flood/predict",
            json={
                "latitude": request.latitude,
                "longitude": request.longitude
            },
            timeout=30
        )

        flood_response.raise_for_status()
        flood_data = flood_response.json()


        landslide_response = requests.post(
            "http://127.0.0.1:8000/landslide/predict",
            json={
                "latitude": request.latitude,
                "longitude": request.longitude
            },
            timeout=30
        )

        landslide_response.raise_for_status()
        landslide_data = landslide_response.json()


        flood_risk = flood_data.get("flood_risk", {})
        landslide_risk = landslide_data.get("landslide_risk", {})


        flood_probability = float(
            flood_risk.get("flood_probability", 0)
        )

        landslide_probability = float(
            landslide_risk.get("landslide_probability", 0)
        )


        combined_probability = max(
            flood_probability,
            landslide_probability
        )


        if combined_probability >= 0.75:
            overall_risk = "EXTREME"
            recommendation = "DO NOT TRAVEL"

        elif combined_probability >= 0.50:
            overall_risk = "HIGH"
            recommendation = "AVOID ROUTE"

        elif combined_probability >= 0.25:
            overall_risk = "MEDIUM"
            recommendation = "TRAVEL WITH CAUTION"

        else:
            overall_risk = "LOW"
            recommendation = "ROUTE APPEARS SAFE"


        return {
            "success": True,

            "location": {
                "latitude": request.latitude,
                "longitude": request.longitude
            },

            "flood": {
                "probability": flood_probability,
                "risk_level": flood_risk.get(
                    "risk_level",
                    "UNKNOWN"
                )
            },

            "landslide": {
                "probability": landslide_probability,
                "risk_level": landslide_risk.get(
                    "risk_level",
                    "UNKNOWN"
                )
            },

            "overall_risk": {
                "probability": round(
                    combined_probability,
                    4
                ),
                "risk_level": overall_risk
            },

            "recommendation": recommendation
        }


    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Risk analysis failed: {str(e)}"
        )

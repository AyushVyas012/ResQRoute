from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.routing_service import get_routes


router = APIRouter(
    prefix="/routes",
    tags=["Routes"]
)


class RouteRequest(BaseModel):
    start_latitude: float
    start_longitude: float
    destination_latitude: float
    destination_longitude: float


@router.post("/find")
def find_routes(request: RouteRequest):

    try:
        routes = get_routes(
            request.start_latitude,
            request.start_longitude,
            request.destination_latitude,
            request.destination_longitude
        )

        return {
            "success": True,
            "start": {
                "latitude": request.start_latitude,
                "longitude": request.start_longitude
            },
            "destination": {
                "latitude": request.destination_latitude,
                "longitude": request.destination_longitude
            },
            "routes": routes
        }

    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Routing failed: {str(e)}"
        )
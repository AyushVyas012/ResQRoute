from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.emergency_service import get_nearest_services
from app.services.routing_service import get_routes
from app.ml.route_risk import score_routes


router = APIRouter(
    prefix="/emergency",
    tags=["Emergency Response"]
)


class EmergencyLocation(BaseModel):
    latitude: float
    longitude: float


@router.post("/nearby")
def nearby_emergency_services(
    location: EmergencyLocation
):
    """
    Find nearby police, hospitals and fire stations.
    """

    try:

        services = get_nearest_services(
            location.latitude,
            location.longitude
        )

        return {
            "success": True,

            "location": {
                "latitude": location.latitude,
                "longitude": location.longitude
            },

            "services": services
        }

    except Exception as e:

        raise HTTPException(
            status_code=503,
            detail=f"Emergency service search failed: {str(e)}"
        )


@router.post("/accident")
def report_accident(
    location: EmergencyLocation
):
    """
    Report an accident.

    Flow:

    GPS
      ↓
    Nearby emergency services
      ↓
    Nearest hospital
      ↓
    OSRM routes
      ↓
    Route ML scoring
      ↓
    Best emergency route
    """

    try:

        # --------------------------------
        # 1. Find emergency services
        # --------------------------------

        services = get_nearest_services(
            location.latitude,
            location.longitude
        )

        # --------------------------------
        # 2. Get nearest hospital
        # --------------------------------

        hospital = services.get("hospital")

        if hospital is None:

            return {
                "success": True,

                "alert": {
                    "type": "ACCIDENT",
                    "severity": "CRITICAL",
                    "message": (
                        "Accident reported, "
                        "but no nearby hospital was found."
                    )
                },

                "location": {
                    "latitude": location.latitude,
                    "longitude": location.longitude
                },

                "services": services,

                "hospital_route": None,

                "emergency_number": "112"
            }

        # --------------------------------
        # 3. Get road routes using OSRM
        # --------------------------------

        routes = get_routes(
            location.latitude,
            location.longitude,
            hospital["latitude"],
            hospital["longitude"]
        )

        # --------------------------------
        # 4. Score routes using ML
        # --------------------------------

        scored_routes = score_routes(
            routes
        )

        # --------------------------------
        # 5. Select best route
        # --------------------------------

        best_route = (
            scored_routes[0]
            if scored_routes
            else None
        )

        # --------------------------------
        # 6. Prepare hospital route
        # --------------------------------

        hospital_route = {

            "available": best_route is not None,

            "route_id": (
                best_route["route_id"]
                if best_route
                else None
            ),

            "distance_km": (
                best_route["distance_km"]
                if best_route
                else None
            ),

            "duration_minutes": (
                best_route["duration_minutes"]
                if best_route
                else None
            ),

            # ML information
            "ml_predicted_time_min": (
                best_route["ml_predicted_time_min"]
                if best_route
                else None
            ),

            "estimated_speed_kmph": (
                best_route["estimated_speed_kmph"]
                if best_route
                else None
            ),

            "traffic_level_estimate": (
                best_route["traffic_level_estimate"]
                if best_route
                else None
            ),

            "emergency_score": (
                best_route["emergency_score"]
                if best_route
                else None
            ),

            "emergency_rank": (
                best_route["emergency_rank"]
                if best_route
                else None
            ),

            # Map geometry
            "geometry": (
                best_route["geometry"]
                if best_route
                else None
            ),

            # Navigation steps
            "steps": (
                best_route["steps"]
                if best_route
                else []
            )
        }

        # --------------------------------
        # 7. Return complete response
        # --------------------------------

        return {

            "success": True,

            "alert": {
                "type": "ACCIDENT",
                "severity": "CRITICAL",
                "message": (
                    "Accident reported. "
                    "Nearby emergency services identified "
                    "and the best hospital route was selected "
                    "using Route ML."
                )
            },

            "location": {
                "latitude": location.latitude,
                "longitude": location.longitude
            },

            "hospital": {
                "name": hospital["name"],
                "latitude": hospital["latitude"],
                "longitude": hospital["longitude"],
                "distance_km": hospital["distance_km"],
                "phone": hospital.get("phone")
            },

            "hospital_route": hospital_route,

            # All routes with ML scores
            "all_routes": scored_routes,

            # Nearby police / hospital / fire
            "services": services,

            # India emergency number
            "emergency_number": "112"
        }

    except Exception as e:

        raise HTTPException(
            status_code=503,
            detail=f"Emergency routing failed: {str(e)}"
        )
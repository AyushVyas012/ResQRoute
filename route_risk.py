from pathlib import Path
from datetime import datetime

import joblib
import pandas as pd


# ============================================================
# MODEL PATH
# ============================================================
#
# Current file:
# ResQRoute/backend/app/ml/route_risk.py
#
# parents[0] -> app/ml
# parents[1] -> app
# parents[2] -> backend
# parents[3] -> ResQRoute
#
# Model:
# ResQRoute/models/trained/route_time_model.joblib
#

MODEL_PATH = (
    Path(__file__).resolve().parents[3]
    / "models"
    / "trained"
    / "route_time_model.joblib"
)


# Model artifact loaded once and reused
_artifact = None


# ============================================================
# LOAD MODEL
# ============================================================

def _load_model():
    """
    Load the trained Route ML model.

    The model is loaded only once to avoid loading
    the .joblib file for every API request.
    """

    global _artifact

    if _artifact is None:

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Route ML model not found: {MODEL_PATH}"
            )

        _artifact = joblib.load(MODEL_PATH)

    return _artifact


# ============================================================
# TRAFFIC ESTIMATION
# ============================================================

def _traffic_from_speed(speed_kmph: float) -> str:
    """
    Estimate traffic level from route speed.

    IMPORTANT:
    This is a prototype heuristic.
    It is NOT live traffic data.
    """

    if speed_kmph < 15:
        return "Very High"

    if speed_kmph < 25:
        return "High"

    if speed_kmph < 40:
        return "Medium"

    return "Low"


# ============================================================
# SCORE ROUTES
# ============================================================

def score_routes(
    routes,
    hour=None,
    day_of_week=None
):
    """
    Score routes using the trained Route ML model.

    Input:
        routes:
            List of routes returned by OSRM.

    Optional:
        hour:
            Hour of day, 0-23.

        day_of_week:
            Example: Monday, Tuesday, etc.

    Output:
        List of routes containing:

        - original OSRM route information
        - ML predicted travel time
        - estimated speed
        - traffic estimate
        - emergency score
        - emergency rank
    """

    # No routes
    if not routes:
        return []


    # --------------------------------------------------------
    # Load trained model
    # --------------------------------------------------------

    artifact = _load_model()

    model = artifact["model"]
    preprocessor = artifact["preprocessor"]


    # --------------------------------------------------------
    # Get current time
    # --------------------------------------------------------

    now = datetime.now()

    if hour is None:
        hour = now.hour

    if day_of_week is None:
        day_of_week = now.strftime("%A")


    # --------------------------------------------------------
    # Store scored routes
    # --------------------------------------------------------

    scored_routes = []


    # ========================================================
    # PROCESS EACH ROUTE
    # ========================================================

    for route in routes:

        # ----------------------------------------------------
        # Route distance
        # ----------------------------------------------------

        distance = float(
            route["distance_km"]
        )


        # ----------------------------------------------------
        # OSRM route duration
        # ----------------------------------------------------

        duration = float(
            route["duration_minutes"]
        )


        # ----------------------------------------------------
        # Calculate estimated speed
        # ----------------------------------------------------

        if duration > 0:

            speed = (
                distance
                / (duration / 60.0)
            )

        else:

            speed = 5.0


        # ----------------------------------------------------
        # Estimate traffic level
        # ----------------------------------------------------

        traffic = _traffic_from_speed(
            speed
        )


        # ----------------------------------------------------
        # Prepare features
        #
        # These MUST match the features used during training.
        # ----------------------------------------------------

        features = pd.DataFrame([
            {
                "distance_km": distance,

                "traffic_level": traffic,

                "avg_speed_kmph": speed,

                "hour": int(hour),

                "day_of_week": str(
                    day_of_week
                )
            }
        ])


        # ----------------------------------------------------
        # Apply training preprocessing
        # ----------------------------------------------------

        processed_features = (
            preprocessor.transform(
                features
            )
        )


        # ----------------------------------------------------
        # Predict route time using ML
        # ----------------------------------------------------

        predicted_time = float(
            model.predict(
                processed_features
            )[0]
        )


        # ----------------------------------------------------
        # Emergency route score
        #
        # Lower score = better route.
        #
        # 65% -> actual OSRM duration
        # 35% -> ML predicted duration
        # ----------------------------------------------------

        emergency_score = (
            0.65 * duration
            + 0.35 * predicted_time
        )


        # ----------------------------------------------------
        # Add ML information to route
        # ----------------------------------------------------

        scored_routes.append({

            # Keep original OSRM information
            **route,


            # ML prediction
            "ml_predicted_time_min": round(
                predicted_time,
                2
            ),


            # Calculated route speed
            "estimated_speed_kmph": round(
                speed,
                2
            ),


            # Prototype traffic estimate
            "traffic_level_estimate": traffic,


            # Combined emergency score
            "emergency_score": round(
                emergency_score,
                2
            )
        })


    # ========================================================
    # SORT ROUTES
    # ========================================================
    #
    # Lowest emergency score = best route.
    #

    scored_routes.sort(
        key=lambda route:
        route["emergency_score"]
    )


    # ========================================================
    # ASSIGN RANK
    # ========================================================

    for rank, route in enumerate(
        scored_routes,
        start=1
    ):

        route["emergency_rank"] = rank


    return scored_routes


# ============================================================
# BEST ROUTE
# ============================================================

def best_route(
    routes,
    hour=None,
    day_of_week=None
):
    """
    Return the best route according to
    the Route ML scoring system.
    """

    scored_routes = score_routes(
        routes,
        hour,
        day_of_week
    )


    if not scored_routes:
        return None


    return scored_routes[0]
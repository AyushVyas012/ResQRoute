import os
import joblib
import pandas as pd


# Project root:
# ResQRoute/
# ├── backend/
# │   └── app/ml/flood_model.py
# └── models/trained/flood_model.joblib

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(__file__)
        )
    )
)

MODEL_PATH = os.path.join(
    PROJECT_ROOT,
    "models",
    "trained",
    "flood_model.joblib"
)


# Load trained model
_model_package = joblib.load(MODEL_PATH)

model = _model_package["model"]
threshold = _model_package["threshold"]
features = _model_package["features"]


def predict_flood_risk(data: dict):
    """
    Predict flood probability and risk level.
    """

    # Create dataframe using the exact training feature order
    input_data = pd.DataFrame(
        [[data[feature] for feature in features]],
        columns=features
    )

    # Get probability of flood
    probability = float(
        model.predict_proba(input_data)[0][1]
    )

    # Safety-oriented risk levels
    if probability >= 0.50:
        risk_level = "EXTREME"

    elif probability >= 0.25:
        risk_level = "HIGH"

    elif probability >= threshold:
        risk_level = "MEDIUM"

    else:
        risk_level = "LOW"

    return {
        "flood_probability": round(probability, 4),
        "risk_level": risk_level,
        "model_threshold": threshold
    }

import os
import joblib
import pandas as pd


MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "models",
    "trained",
    "landslide_model.joblib"
)


# Load trained model
_model_package = joblib.load(MODEL_PATH)

model = _model_package["model"]
features = _model_package["features"]
threshold = _model_package["threshold"]


def predict_landslide_risk(data: dict):

    # Create dataframe using the exact training feature order
    input_data = pd.DataFrame(
        [[data[feature] for feature in features]],
        columns=features
    )

    # Probability of landslide
    probability = float(
        model.predict_proba(input_data)[0][1]
    )

    # Risk classification
    if probability >= 0.75:
        risk_level = "EXTREME"

    elif probability >= 0.50:
        risk_level = "HIGH"

    elif probability >= threshold:
        risk_level = "MEDIUM"

    else:
        risk_level = "LOW"

    return {
        "landslide_probability": round(probability, 4),
        "risk_level": risk_level,
        "model_threshold": threshold
    }

from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder


BASE = Path(__file__).resolve().parents[1]

DATA_PATH = (
    BASE
    / "data"
    / "processed"
    / "dummy_routing_dataset.csv"
)

MODEL_PATH = (
    BASE.parent
    / "models"
    / "trained"
    / "route_time_model.joblib"
)


FEATURES = [
    "distance_km",
    "traffic_level",
    "avg_speed_kmph",
    "hour",
    "day_of_week",
]

TARGET = "route_time_min"


def main():

    print("Loading dataset...")

    df = pd.read_csv(DATA_PATH)

    print(f"Dataset rows: {len(df)}")

    X = df[FEATURES]
    y = df[TARGET]

    categorical_features = [
        "traffic_level",
        "day_of_week",
    ]

    numerical_features = [
        "distance_km",
        "avg_speed_kmph",
        "hour",
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                categorical_features,
            ),
            (
                "numerical",
                "passthrough",
                numerical_features,
            ),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)

    model = RandomForestRegressor(
        n_estimators=500,
        max_depth=18,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )

    print("Training Route ML model...")

    model.fit(
        X_train_processed,
        y_train,
    )

    predictions = model.predict(
        X_test_processed
    )

    mae = mean_absolute_error(
        y_test,
        predictions,
    )

    r2 = r2_score(
        y_test,
        predictions,
    )

    print()
    print("==============================")
    print("ROUTE ML TRAINING RESULTS")
    print("==============================")
    print(f"MAE: {mae:.3f} minutes")
    print(f"R2 Score: {r2:.4f}")

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    artifact = {
        "model": model,
        "preprocessor": preprocessor,
        "features": FEATURES,
        "target": TARGET,
        "mae_minutes": float(mae),
        "r2": float(r2),
    }

    joblib.dump(
        artifact,
        MODEL_PATH,
    )

    print()
    print("Model saved successfully:")
    print(MODEL_PATH)


if __name__ == "__main__":
    main()
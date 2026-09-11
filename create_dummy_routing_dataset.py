import random
from datetime import datetime, timedelta
import pandas as pd


random.seed(42)

ROWS = 1000

start_time = datetime(2026, 1, 1, 0, 0, 0)

traffic_levels = ["Low", "Medium", "High", "Very High"]
route_types = ["Highway", "Urban", "Residential", "Mixed"]

rows = []

for i in range(ROWS):

    timestamp = start_time + timedelta(
        minutes=random.randint(0, 60 * 24 * 180)
    )

    source_lat = random.uniform(28.50, 28.70)
    source_lon = random.uniform(77.10, 77.40)

    destination_lat = random.uniform(28.50, 28.70)
    destination_lon = random.uniform(77.10, 77.40)

    distance_km = random.uniform(2, 40)

    traffic_level = random.choices(
        traffic_levels,
        weights=[30, 36, 23, 11]
    )[0]

    speed_ranges = {
        "Low": (40, 65),
        "Medium": (25, 40),
        "High": (15, 25),
        "Very High": (7, 15)
    }

    min_speed, max_speed = speed_ranges[traffic_level]

    avg_speed_kmph = random.uniform(
        min_speed,
        max_speed
    )

    route_time_min = (
        distance_km / avg_speed_kmph
    ) * 60

    route_time_min += random.uniform(-2, 2)

    route_time_min = max(
        route_time_min,
        1
    )

    rows.append({
        "trip_id": i + 1,
        "timestamp": timestamp,
        "source_lat": round(source_lat, 6),
        "source_lon": round(source_lon, 6),
        "destination_lat": round(destination_lat, 6),
        "destination_lon": round(destination_lon, 6),
        "distance_km": round(distance_km, 2),
        "traffic_level": traffic_level,
        "avg_speed_kmph": round(avg_speed_kmph, 2),
        "route_time_min": round(route_time_min, 2),
        "hour": timestamp.hour,
        "day_of_week": timestamp.strftime("%A"),
        "route_type": random.choice(route_types)
    })


df = pd.DataFrame(rows)

output = "data/processed/dummy_routing_dataset.csv"

df.to_csv(
    output,
    index=False
)

print(f"Dataset created: {output}")
print(f"Rows: {len(df)}")
print("\nColumns:")
print(list(df.columns))

print("\nTraffic distribution:")
print(df["traffic_level"].value_counts())

print("\nFirst 5 rows:")
print(df.head())
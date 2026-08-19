"""
Retrain Random Forest and Isolation Forest models on the U.S. EPA AQI (0–500).

This script:
1. Reads all data from the air_quality table (which now includes calculated_aqi).
2. Computes time features (hour, day) exactly like the preprocessing notebook.
3. Trains a RandomForestRegressor to predict calculated_aqi from pollutant + time features.
4. Trains an IsolationForest on calculated_aqi + pollutant features for anomaly detection.
5. Saves both models to ML/saved_models/.

Usage:
    cd <project_root>
    venv/Scripts/python ML/train_aqi500.py
"""

import os
import sys
import sqlite3

import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "database", "air_quality.db")
MODELS_DIR = os.path.join(PROJECT_ROOT, "ML", "saved_models")


def load_and_preprocess():
    """Load air_quality data and add time features."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM air_quality", conn)
    conn.close()

    print(f"Loaded {len(df)} rows from air_quality table")

    # Add time features (same as preprocessing notebook)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour"] = df["timestamp"].dt.hour
    df["day"] = df["timestamp"].dt.day

    # Drop rows with missing calculated_aqi
    df = df.dropna(subset=["calculated_aqi"])
    print(f"After dropping NaN calculated_aqi: {len(df)} rows")

    return df


def train_random_forest(df):
    """Train Random Forest on calculated_aqi (0–500)."""
    print("\n" + "=" * 60)
    print("Training Random Forest Regressor (EPA AQI 0–500)")
    print("=" * 60)

    feature_cols = ["pm2_5", "pm10", "co", "no2", "o3", "so2", "hour", "day"]
    X = df[feature_cols]
    y = df["calculated_aqi"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    pred = rf.predict(X_test)

    mae = mean_absolute_error(y_test, pred)
    rmse = mean_squared_error(y_test, pred) ** 0.5
    r2 = r2_score(y_test, pred)

    print(f"MAE:  {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")
    print(f"R2:   {r2:.4f}")

    # Feature importance
    importance = pd.DataFrame({
        "Feature": feature_cols,
        "Importance": rf.feature_importances_,
    }).sort_values("Importance", ascending=False)
    print("\nFeature Importances:")
    for _, row in importance.iterrows():
        print(f"  {row['Feature']:8s} {row['Importance']:.6f}")

    # Save
    path = os.path.join(MODELS_DIR, "random_forest_aqi_500.pkl")
    joblib.dump(rf, path)
    print(f"\nSaved to {path}")

    # Verify
    loaded = joblib.load(path)
    print(f"Verified feature_names_in_: {list(loaded.feature_names_in_)}")

    return rf


def train_isolation_forest(df):
    """Train Isolation Forest on calculated_aqi + pollutant features."""
    print("\n" + "=" * 60)
    print("Training Isolation Forest (EPA AQI 0–500)")
    print("=" * 60)

    feature_cols = ["calculated_aqi", "pm2_5", "pm10", "co", "no2", "o3", "so2"]
    X = df[feature_cols]

    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    model.fit(X)

    predictions = model.predict(X)
    n_normal = (predictions == 1).sum()
    n_anomaly = (predictions == -1).sum()
    print(f"Normal readings: {n_normal}")
    print(f"Anomalous readings: {n_anomaly}")
    print(f"Anomaly rate: {n_anomaly / len(predictions) * 100:.1f}%")

    # Save
    path = os.path.join(MODELS_DIR, "isolation_forest_aqi_500.pkl")
    joblib.dump(model, path)
    print(f"\nSaved to {path}")

    # Verify
    loaded = joblib.load(path)
    print(f"Verified feature_names_in_: {list(loaded.feature_names_in_)}")

    return model


if __name__ == "__main__":
    os.makedirs(MODELS_DIR, exist_ok=True)
    df = load_and_preprocess()
    train_random_forest(df)
    train_isolation_forest(df)
    print("\nDone!")

from __future__ import annotations

import os

import joblib
import pandas as pd

from driver_team_circuit_constants import F1_2026_TRACKS
from prediction_context import apply_qualifying_context, latest_2026_driver_snapshot


def make_pi_prediction(gp_name: str, year: int = 2026, rain: int = 0):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    model_path = os.path.join(project_root, "models", "f1_optuna_pi_model.pkl")
    features_path = os.path.join(project_root, "models", "f1_optuna_feature_names.pkl")
    data_path = os.path.join(project_root, "dataset", "f1_final_features.csv")

    if gp_name not in F1_2026_TRACKS:
        return f"Invalid Grand Prix: {gp_name}"

    try:
        model = joblib.load(model_path)
        feature_names = joblib.load(features_path)
    except FileNotFoundError:
        return "Model files were not found. Train the model before running predictions."

    df = pd.read_csv(data_path)
    latest_stats = latest_2026_driver_snapshot(df)
    latest_stats = apply_qualifying_context(
        latest_stats,
        df,
        track_name=gp_name,
        rain_status=rain,
    )
    latest_stats["Year"] = year

    x_pred = pd.get_dummies(latest_stats, columns=["GP", "Track_Type", "Track_DNA"])
    x_pred = x_pred.reindex(columns=feature_names, fill_value=0)

    latest_stats["AI_Score"] = model.predict(x_pred)
    results = latest_stats[["Driver", "Team", "AI_Score"]].sort_values(
        by="AI_Score",
        ascending=False,
    )
    results["Rank"] = range(1, len(results) + 1)
    return results


if __name__ == "__main__":
    target_gp = "Monaco"
    weather_condition = 0

    prediction_table = make_pi_prediction(target_gp, rain=weather_condition)
    if isinstance(prediction_table, str):
        print(prediction_table)
    else:
        print(prediction_table[["Rank", "Driver", "Team", "AI_Score"]].to_string(index=False))

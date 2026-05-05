import os
import sys

import joblib
import numpy as np
import pandas as pd


current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from driver_team_circuit_constants import F1_2026_TRACKS
from prediction_context import (
    apply_race_context,
    blended_race_scores,
    latest_2026_driver_snapshot,
)


def softmax(x, temperature=0.06):
    exp_scores = np.exp((x - np.max(x)) / temperature)
    return exp_scores / exp_scores.sum()


def get_race_probabilities(gp_name, rain_status=0):
    project_root = os.path.dirname(current_dir)
    model_file = os.path.join(project_root, "models", "f1_optuna_race_pace_model.pkl")
    features_file = os.path.join(project_root, "models", "f1_optuna_race_feature_names.pkl")
    data_file = os.path.join(project_root, "rdataset", "f1_final_race_features.csv")

    if gp_name not in F1_2026_TRACKS:
        return None

    model = joblib.load(model_file)
    feature_names = joblib.load(features_file)
    df = pd.read_csv(data_file)

    predict_df = latest_2026_driver_snapshot(df)
    predict_df = apply_race_context(
        predict_df,
        df,
        track_name=gp_name,
        rain_status=rain_status,
    )

    X = pd.get_dummies(predict_df, columns=["GP", "Track_Type", "Track_DNA"])
    X = X.reindex(columns=feature_names, fill_value=0)

    scores = blended_race_scores(model.predict(X), predict_df)
    predict_df["Probability"] = softmax(scores) * 100

    return predict_df[["Driver", "Team", "Probability"]].sort_values(
        by="Probability", ascending=False
    )


if __name__ == "__main__":
    gp = input("Grand Prix adini gir: ")
    rain = int(input("Yagmur (0/1): "))
    probs = get_race_probabilities(gp, rain_status=rain)
    if probs is None:
        print("Gecersiz pist secimi.")
    else:
        print(probs.head(10).to_string(index=False))

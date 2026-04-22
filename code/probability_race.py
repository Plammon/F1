import os
import sys

import joblib
import numpy as np
import pandas as pd


current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from driver_team_circuit_constants import F1_2026_TRACKS


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

    active_drivers = df[df["Year"] == 2026]["Driver"].unique()
    predict_df = (
        df[df["Driver"].isin(active_drivers)]
        .sort_values(["Year", "GP"])
        .groupby("Driver")
        .last()
        .reset_index()
    )

    predict_df["GP"] = gp_name
    predict_df["Rain"] = rain_status
    predict_df["Year"] = 2026
    predict_df["Track_Type"] = F1_2026_TRACKS[gp_name]["Type"]
    predict_df["Track_DNA"] = F1_2026_TRACKS[gp_name]["DNA"]

    if "Grid_Pos" in predict_df.columns:
        predict_df["Grid_Pos"] = predict_df["Grid_Pos"].fillna(predict_df["Grid_Size"])

    X = pd.get_dummies(predict_df, columns=["GP", "Track_Type", "Track_DNA"])
    X = X.reindex(columns=feature_names, fill_value=0)

    scores = model.predict(X)
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

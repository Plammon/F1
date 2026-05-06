import os
import sys

import joblib
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


def get_f1_race_prediction(gp_name, rain_status=0):
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

    predict_df["AI_Race_Score"] = blended_race_scores(model.predict(X), predict_df)
    final_list = predict_df[["Driver", "Team", "AI_Race_Score"]].sort_values(
        by="AI_Race_Score", ascending=False
    )
    final_list["Rank"] = range(1, len(final_list) + 1)
    return final_list


if __name__ == "__main__":
    gp = input("Grand Prix adini gir: ")
    rain = int(input("Yagmur (0/1): "))
    result = get_f1_race_prediction(gp, rain_status=rain)
    if result is None:
        print("Gecersiz pist secimi.")
    else:
        print(result[["Rank", "Driver", "Team", "AI_Race_Score"]].to_string(index=False))

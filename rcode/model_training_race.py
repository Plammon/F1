import os

import joblib
import numpy as np
import optuna
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import TimeSeriesSplit


def objective(trial, X, y, weights):
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 400, 1400),
        "max_depth": trial.suggest_int("max_depth", 3, 9),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.1, log=True),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
        "reg_alpha": trial.suggest_float("reg_alpha", 0.0, 1.0),
        "reg_lambda": trial.suggest_float("reg_lambda", 0.0, 3.0),
        "objective": "reg:squarederror",
        "random_state": 42,
        "n_jobs": -1,
    }

    tscv = TimeSeriesSplit(n_splits=3)
    errors = []

    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        w_train = weights[train_idx]

        model = xgb.XGBRegressor(**params)
        model.fit(X_train, y_train, sample_weight=w_train)
        preds = model.predict(X_test)
        errors.append(mean_absolute_error(y_test, preds))

    return float(np.mean(errors))


def train_race_model(input_path, n_trials=50):
    df = pd.read_csv(input_path)
    df = df.sort_values(["Year", "GP"]).reset_index(drop=True)

    # Race tarafinda hedef olarak pace index kullaniliyor.
    y = df["Race_Pace_Index"]
    feature_cols = [
        "Year",
        "TrackTemp",
        "Rain",
        "Grid_Size",
        "Grid_Pos",
        "DNF_Flag",
        "Gain_From_Grid",
        "Driver_Weighted_Race_Form",
        "Team_Weighted_Race_Form",
        "Driver_Track_Race_Form",
        "Overtake_Trend",
        "DNF_Recent_Rate",
        "GP",
        "Track_Type",
        "Track_DNA",
    ]
    X = pd.get_dummies(df[feature_cols], columns=["GP", "Track_Type", "Track_DNA"])

    # 2026 verisine daha yuksek agirlik ver.
    weights = np.where(df["Year"] == 2026, 5.0, 1.0)

    print("Optuna race modeli icin en iyi parametreleri ariyor...")
    study = optuna.create_study(direction="minimize")
    study.optimize(lambda trial: objective(trial, X, y, weights), n_trials=n_trials)

    print(f"En iyi CV MAE: {study.best_value:.5f}")
    best_model = xgb.XGBRegressor(**study.best_params)
    best_model.fit(X, y, sample_weight=weights)

    return best_model, X.columns


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)

    input_path = os.path.join(project_root, "rdataset", "f1_final_race_features.csv")
    model_dir = os.path.join(project_root, "models")
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    model, feature_names = train_race_model(input_path, n_trials=50)

    model_path = os.path.join(model_dir, "f1_optuna_race_pace_model.pkl")
    features_path = os.path.join(model_dir, "f1_optuna_race_feature_names.pkl")

    joblib.dump(model, model_path)
    joblib.dump(feature_names, features_path)
    print(f"Race modeli kaydedildi: {model_path}")
    print(f"Race feature listesi kaydedildi: {features_path}")

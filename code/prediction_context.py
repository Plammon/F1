"""Scenario preparation helpers for model inference."""

from __future__ import annotations

import pandas as pd

from driver_team_circuit_constants import F1_2026_TRACKS, get_model_gp_name

RACE_SCENARIO_BLEND_WEIGHT = 0.25


def latest_2026_driver_snapshot(df: pd.DataFrame) -> pd.DataFrame:
    active_drivers = df.loc[df["Year"] == 2026, "Driver"].unique()
    return (
        df[df["Driver"].isin(active_drivers)]
        .sort_values(["Year", "GP"])
        .groupby("Driver")
        .last()
        .reset_index()
    )


def scenario_track_temperature(
    df: pd.DataFrame,
    *,
    model_gp: str,
    track_type: str,
    rain_status: int,
) -> float:
    filters = [
        (df["GP"].eq(model_gp) & df["Track_Type"].eq(track_type) & df["Rain"].eq(rain_status)),
        (df["Track_Type"].eq(track_type) & df["Rain"].eq(rain_status)),
        df["Rain"].eq(rain_status),
    ]
    for mask in filters:
        value = df.loc[mask, "TrackTemp"].median()
        if pd.notna(value):
            return float(value)
    fallback = df["TrackTemp"].median()
    return float(fallback) if pd.notna(fallback) else (21.0 if rain_status else 34.0)


def driver_context_average(
    df: pd.DataFrame,
    *,
    value_column: str,
    track_type: str,
    rain_status: int,
    drivers: pd.Series,
) -> pd.Series:
    exact = (
        df[df["Track_Type"].eq(track_type) & df["Rain"].eq(rain_status)]
        .groupby("Driver")[value_column]
        .mean()
    )
    driver_fallback = df.groupby("Driver")[value_column].mean()
    global_fallback = df[value_column].mean()
    return (
        drivers.map(exact)
        .fillna(drivers.map(driver_fallback))
        .fillna(0.0 if pd.isna(global_fallback) else float(global_fallback))
    )


def apply_qualifying_context(
    predict_df: pd.DataFrame,
    history_df: pd.DataFrame,
    *,
    track_name: str,
    rain_status: int,
) -> pd.DataFrame:
    track = F1_2026_TRACKS[track_name]
    model_gp = get_model_gp_name(track_name, "qualifying")

    predict_df = predict_df.copy()
    predict_df["GP"] = model_gp
    predict_df["Rain"] = rain_status
    predict_df["Year"] = 2026
    predict_df["Track_Type"] = track["Type"]
    predict_df["Track_DNA"] = track["DNA"]
    predict_df["TrackTemp"] = scenario_track_temperature(
        history_df,
        model_gp=model_gp,
        track_type=track["Type"],
        rain_status=rain_status,
    )
    predict_df["Track_Weather_Specialty"] = driver_context_average(
        history_df,
        value_column="Performance_Index",
        track_type=track["Type"],
        rain_status=rain_status,
        drivers=predict_df["Driver"],
    )
    return predict_df


def apply_race_context(
    predict_df: pd.DataFrame,
    history_df: pd.DataFrame,
    *,
    track_name: str,
    rain_status: int,
) -> pd.DataFrame:
    track = F1_2026_TRACKS[track_name]
    model_gp = get_model_gp_name(track_name, "race")

    predict_df = predict_df.copy()
    predict_df["GP"] = model_gp
    predict_df["Rain"] = rain_status
    predict_df["Year"] = 2026
    predict_df["Track_Type"] = track["Type"]
    predict_df["Track_DNA"] = track["DNA"]
    predict_df["TrackTemp"] = scenario_track_temperature(
        history_df,
        model_gp=model_gp,
        track_type=track["Type"],
        rain_status=rain_status,
    )
    predict_df["Driver_Track_Race_Form"] = driver_context_average(
        history_df,
        value_column="Race_Pace_Index",
        track_type=track["Type"],
        rain_status=rain_status,
        drivers=predict_df["Driver"],
    )
    if "Grid_Pos" in predict_df.columns:
        predict_df["Grid_Pos"] = predict_df["Grid_Pos"].fillna(predict_df["Grid_Size"])
    return predict_df


def blended_race_scores(raw_scores, predict_df: pd.DataFrame) -> pd.Series:
    """Blend XGBoost race output with the existing engineered scenario prior."""
    raw = pd.Series(raw_scores, index=predict_df.index, dtype=float)
    scenario_prior = (
        0.65 * predict_df["Driver_Track_Race_Form"].astype(float)
        + 0.25 * predict_df["Driver_Weighted_Race_Form"].astype(float)
        + 0.10 * predict_df["Team_Weighted_Race_Form"].astype(float)
        + 0.012 * predict_df["Overtake_Trend"].astype(float)
        - 0.040 * predict_df["DNF_Recent_Rate"].astype(float)
    )
    return raw + RACE_SCENARIO_BLEND_WEIGHT * (scenario_prior - scenario_prior.mean())

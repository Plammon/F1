import os

import pandas as pd


def generate_race_features(input_path, output_path):
    df = pd.read_csv(input_path)
    df = df.sort_values(by=["Year", "GP", "Driver"]).reset_index(drop=True)

    def ewma_form(series):
        return series.ewm(alpha=0.3, adjust=False).mean().shift(1)

    df["Driver_Weighted_Race_Form"] = df.groupby("Driver")["Race_Pace_Index"].transform(ewma_form)
    df["Team_Weighted_Race_Form"] = df.groupby("Team")["Race_Pace_Index"].transform(ewma_form)

    df["Driver_Track_Race_Form"] = df.groupby(["Driver", "Track_Type", "Rain"])["Race_Pace_Index"].transform(
        lambda x: x.expanding().mean().shift(1)
    )

    df["Overtake_Trend"] = df.groupby("Driver")["Gain_From_Grid"].transform(
        lambda x: x.rolling(window=5, min_periods=1).mean().diff().shift(1)
    )
    df["DNF_Recent_Rate"] = df.groupby("Driver")["DNF_Flag"].transform(
        lambda x: x.rolling(window=10, min_periods=1).mean().shift(1)
    )

    fill_cols = [
        "Driver_Weighted_Race_Form",
        "Team_Weighted_Race_Form",
        "Driver_Track_Race_Form",
        "Overtake_Trend",
        "DNF_Recent_Rate",
    ]
    for col in fill_cols:
        df[col] = df[col].fillna(0)

    df.to_csv(output_path, index=False)
    return df


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    rdataset_dir = os.path.join(project_root, "rdataset")

    input_path = os.path.join(rdataset_dir, "f1_processed_race_readable.csv")
    output_path = os.path.join(rdataset_dir, "f1_final_race_features.csv")
    final_df = generate_race_features(input_path, output_path)
    print(f"Feature engineering tamamlandi: {len(final_df.columns)} kolon")

import os

import pandas as pd


def preprocess_race_data(input_csv, output_csv):
    df = pd.read_csv(input_csv)

    df["Grid_Size"] = df.groupby(["Year", "GP"])["Driver"].transform("count")
    df["Grid_Pos"] = pd.to_numeric(df["Grid_Pos"], errors="coerce")
    df["Final_Pos"] = pd.to_numeric(df["Final_Pos"], errors="coerce")
    df["Points"] = pd.to_numeric(df["Points"], errors="coerce").fillna(0)

    # DNF veya diskalifiye gibi durumlar icin pozisyon eksikse grid sonuna at.
    df["Final_Pos"] = df["Final_Pos"].fillna(df["Grid_Size"])
    df["Grid_Pos"] = df["Grid_Pos"].fillna(df["Grid_Size"])

    df["DNF_Flag"] = (
        df["Status"]
        .astype(str)
        .str.contains("Finished|\\+", case=False, regex=True)
        .map({True: 0, False: 1})
    )
    df["Gain_From_Grid"] = df["Grid_Pos"] - df["Final_Pos"]
    df["Race_Pace_Index"] = (df["Grid_Size"] - df["Final_Pos"]) / df["Grid_Size"]

    final_df = df[
        [
            "Year",
            "GP",
            "Track_Type",
            "Track_DNA",
            "Driver",
            "Team",
            "TrackTemp",
            "Rain",
            "Grid_Size",
            "Grid_Pos",
            "Final_Pos",
            "Points",
            "DNF_Flag",
            "Gain_From_Grid",
            "Race_Pace_Index",
        ]
    ].copy()

    final_df.to_csv(output_csv, index=False)
    return final_df


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    rdataset_dir = os.path.join(project_root, "rdataset")

    input_path = os.path.join(rdataset_dir, "f1_master_race_dataset.csv")
    output_path = os.path.join(rdataset_dir, "f1_processed_race_readable.csv")
    df = preprocess_race_data(input_path, output_path)
    print(f"Preprocess tamamlandi: {len(df)} satir")

import glob
import os

import pandas as pd


def merge_race_csvs(rdataset_dir, output_name="f1_master_race_dataset.csv"):
    pattern = os.path.join(rdataset_dir, "*_race_data_final.csv")
    all_files = sorted(glob.glob(pattern))

    if not all_files:
        print(f"Dosya bulunamadi: {pattern}")
        return None

    frames = [pd.read_csv(file) for file in all_files]
    merged = pd.concat(frames, ignore_index=True)
    if "Year" in merged.columns and "GP" in merged.columns:
        merged = merged.sort_values(["Year", "GP"]).reset_index(drop=True)

    output_path = os.path.join(rdataset_dir, output_name)
    merged.to_csv(output_path, index=False)
    print(f"Kaydedildi: {output_path} ({len(merged)} satir)")
    return output_path


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    rdataset_dir = os.path.join(project_root, "rdataset")
    merge_race_csvs(rdataset_dir)

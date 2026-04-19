import datetime
import os
import sys
import time

import fastf1
import pandas as pd
from tqdm import tqdm


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
rdataset_dir = os.path.join(project_root, "rdataset")
if not os.path.exists(rdataset_dir):
    os.makedirs(rdataset_dir)

code_dir = os.path.join(project_root, "code")
if code_dir not in sys.path:
    sys.path.append(code_dir)

try:
    from driver_team_circuit_constants import F1_2026_TRACKS
except ModuleNotFoundError:
    F1_2026_TRACKS = {}


def normalize_team_name(team):
    mapping = {
        "AlphaTauri": "Racing Bulls",
        "RB": "Racing Bulls",
        "VCARB": "Racing Bulls",
        "Sauber": "Audi (Sauber)",
        "Alfa Romeo": "Audi (Sauber)",
        "Aston Martin Aramco": "Aston Martin",
        "Haas F1 Team": "Haas",
    }
    return mapping.get(team, team)


def _track_meta_from_location(location):
    if location in F1_2026_TRACKS:
        return F1_2026_TRACKS[location]["Type"], F1_2026_TRACKS[location]["DNA"]
    return "Permanent", "Standard"


def collect_race_data(start_year=2022, end_year=2026):
    cache_dir = os.path.join(project_root, ".f1_cache_race")
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    fastf1.Cache.enable_cache(cache_dir)

    for year in range(start_year, end_year + 1):
        rows = []
        print(f"\n--- {year} Race verisi toplaniyor ---")
        try:
            schedule = fastf1.get_event_schedule(year)
            events = schedule[schedule["EventFormat"] != "testing"]
            events = events[events["EventDate"] < datetime.datetime.now()]
        except Exception as exc:
            print(f"{year} takvimi okunamadi: {exc}")
            continue

        for _, event in tqdm(events.iterrows(), total=len(events)):
            try:
                session = fastf1.get_session(year, event["RoundNumber"], "R")
                session.load(laps=False, telemetry=False, weather=True)
                results = session.results.copy()
                weather = session.weather_data
                avg_track_temp = weather["TrackTemp"].mean() if weather is not None else None
                rain = 1 if (weather is not None and weather["Rainfall"].any()) else 0
                track_type, track_dna = _track_meta_from_location(event["Location"])

                for _, driver in results.iterrows():
                    rows.append(
                        {
                            "Year": year,
                            "GP": event["EventName"],
                            "Track_Type": track_type,
                            "Track_DNA": track_dna,
                            "Driver": driver.get("FullName"),
                            "Team": normalize_team_name(driver.get("TeamName")),
                            "Grid_Pos": driver.get("GridPosition"),
                            "Final_Pos": driver.get("Position"),
                            "Points": driver.get("Points"),
                            "Status": driver.get("Status"),
                            "TrackTemp": avg_track_temp,
                            "Rain": rain,
                        }
                    )
                time.sleep(0.2)
            except Exception as exc:
                print(f"Hata ({year} {event['EventName']}): {exc}")

        year_df = pd.DataFrame(rows)
        output_path = os.path.join(rdataset_dir, f"{year}_race_data_final.csv")
        year_df.to_csv(output_path, index=False)
        print(f"Kaydedildi: {output_path} ({len(year_df)} satir)")


if __name__ == "__main__":
    collect_race_data(2022, 2026)

import datetime
import os
import re
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


def _norm(text):
    return re.sub(r"[^a-z0-9]+", " ", str(text).lower()).strip()


TRACK_ALIASES = {
    "melbourne": "Albert Park",
    "albert park": "Albert Park",
    "shanghai": "Shanghai",
    "suzuka": "Suzuka",
    "sakhir": "Sakhir",
    "bahrain": "Sakhir",
    "jeddah": "Jeddah",
    "miami": "Miami",
    "imola": "Imola",
    "emilia romagna": "Imola",
    "monaco": "Monaco",
    "montreal": "Montreal",
    "canadian": "Montreal",
    "barcelona": "Barcelona",
    "catalunya": "Barcelona",
    "red bull ring": "Red Bull Ring",
    "spielberg": "Red Bull Ring",
    "silverstone": "Silverstone",
    "spa": "Spa",
    "spa francorchamps": "Spa",
    "hungaroring": "Hungaroring",
    "zandvoort": "Zandvoort",
    "monza": "Monza",
    "madrid": "Madrid",
    "baku": "Baku",
    "singapore": "Singapore",
    "cota": "COTA",
    "austin": "COTA",
    "mexico city": "Mexico City",
    "interlagos": "Interlagos",
    "sao paulo": "Interlagos",
    "las vegas": "Las Vegas",
    "lusail": "Lusail",
    "qatar": "Lusail",
    "yas marina": "Yas Marina",
    "abu dhabi": "Yas Marina",
}


def _resolve_track_key(event_name, location):
    # 1) Dogrudan constants anahtari ile eslesme
    for candidate in (location, event_name):
        if candidate in F1_2026_TRACKS:
            return candidate

    # 2) Alias tablosu ile eslesme
    normalized_candidates = [_norm(location), _norm(event_name)]
    for candidate in normalized_candidates:
        for alias, canonical in TRACK_ALIASES.items():
            if alias in candidate:
                return canonical

    return None


def _track_meta_from_event(event_name, location):
    track_key = _resolve_track_key(event_name, location)
    if track_key and track_key in F1_2026_TRACKS:
        return track_key, F1_2026_TRACKS[track_key]["Type"], F1_2026_TRACKS[track_key]["DNA"]

    # Fallback: metadata bilinmiyorsa event adini GP olarak koru
    return event_name, "Permanent", "Standard"


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
                gp_key, track_type, track_dna = _track_meta_from_event(
                    event["EventName"], event["Location"]
                )

                for _, driver in results.iterrows():
                    rows.append(
                        {
                            "Year": year,
                            "GP": gp_key,
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

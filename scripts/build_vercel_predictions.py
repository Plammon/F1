from __future__ import annotations

import json
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = ROOT / "code"

if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from driver_team_circuit_constants import F1_2026_TRACKS
from engine import get_f1_prediction
from engine_race import get_f1_race_prediction
from probability import get_probabilities
from probability_race import get_race_probabilities


warnings.filterwarnings("ignore", category=UserWarning, module="xgboost")


def ranking_rows(track: str, mode: str, rain: int) -> list[dict[str, object]]:
    frame = (
        get_f1_race_prediction(track, rain)
        if mode == "race"
        else get_f1_prediction(track, rain)
    )
    if frame is None:
        raise ValueError(f"No ranking returned for {mode}/{track}/{rain}")

    score_column = "AI_Race_Score" if mode == "race" else "AI_Score"
    rows = []
    for _, row in frame.head(22).iterrows():
        rows.append(
            {
                "rank": int(row["Rank"]),
                "driver": str(row["Driver"]),
                "team": str(row["Team"]),
                "score": f"{float(row[score_column]):.4f}",
            }
        )
    return rows


def probability_rows(track: str, mode: str, rain: int) -> list[dict[str, object]]:
    frame = (
        get_race_probabilities(track, rain)
        if mode == "race"
        else get_probabilities(track, rain)
    )
    if frame is None:
        raise ValueError(f"No probabilities returned for {mode}/{track}/{rain}")

    rows = []
    for rank, (_, row) in enumerate(frame.head(10).iterrows(), start=1):
        probability = float(row["Probability"])
        rows.append(
            {
                "rank": rank,
                "driver": str(row["Driver"]),
                "team": str(row["Team"]),
                "probability": f"{probability:.2f}",
                "width": f"{max(2.0, min(probability, 100.0)):.2f}",
            }
        )
    return rows


def build_predictions() -> dict[str, object]:
    payload: dict[str, object] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "calendar": "Official 2026 Formula 1 calendar, 22 rounds",
        "tracks": list(F1_2026_TRACKS.keys()),
        "track_metadata": F1_2026_TRACKS,
        "predictions": {"qualifying": {}, "race": {}},
    }

    predictions = payload["predictions"]
    assert isinstance(predictions, dict)

    for mode in ("qualifying", "race"):
        mode_predictions: dict[str, object] = {}
        for rain in (0, 1):
            rain_predictions = {}
            for track in F1_2026_TRACKS:
                rain_predictions[track] = {
                    "ranking": ranking_rows(track, mode, rain),
                    "probabilities": probability_rows(track, mode, rain),
                }
            mode_predictions[str(rain)] = rain_predictions
        predictions[mode] = mode_predictions

    return payload


def main() -> None:
    output_path = ROOT / "predictions.json"
    output_path.write_text(
        json.dumps(build_predictions(), indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()

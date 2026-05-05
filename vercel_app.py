from __future__ import annotations

import json
import os
import sys
from copy import deepcopy
from datetime import datetime, timezone
from threading import Lock
from pathlib import Path

from flask import Flask, jsonify, request, send_file, send_from_directory
from werkzeug.utils import safe_join


PROJECT_ROOT = Path(__file__).resolve().parent


def _project_file(*parts: str) -> Path:
    candidates = (
        PROJECT_ROOT.joinpath(*parts),
        PROJECT_ROOT.parent.joinpath(*parts),
        Path.cwd().joinpath(*parts),
    )
    return next((path for path in candidates if path.exists()), candidates[0])


WEB_DIST = _project_file("web", "dist")
PREDICTION_PATH = _project_file("predictions.json")
REFRESH_LOCK = Lock()


app = Flask(__name__)

PREDICTION_DATA: dict[str, object] = {}
TRACK_NAMES: list[str] = []
TRACK_SET: set[str] = set()
DEFAULT_TRACK = ""
TRACK_METADATA: dict[str, object] = {}
GENERATED_AT = "unknown"
MODE_LABELS = {
    "qualifying": "Qualifying",
    "race": "Race",
}
VIEW_LABELS = {
    "ranking": "Classification",
    "probabilities": "Win probabilities",
}


def _apply_prediction_data(payload: dict[str, object]) -> None:
    global PREDICTION_DATA, TRACK_NAMES, TRACK_SET, DEFAULT_TRACK, TRACK_METADATA, GENERATED_AT

    tracks = list(payload["tracks"])
    PREDICTION_DATA = payload
    TRACK_NAMES = tracks
    TRACK_SET = set(tracks)
    DEFAULT_TRACK = tracks[0]
    TRACK_METADATA = payload.get("track_metadata", {})
    GENERATED_AT = payload.get("generated_at_utc", "unknown")


def _load_prediction_data() -> dict[str, object]:
    return json.loads(PREDICTION_PATH.read_text(encoding="utf-8"))


def _prediction_response(selected_track: str, mode: str, rain: bool, view: str):
    rows = _prediction_rows(selected_track, mode, rain, view)
    return jsonify(
        {
            "track": selected_track,
            "event": TRACK_METADATA.get(selected_track, {}).get("Event", selected_track),
            "mode": mode,
            "weather": "wet" if rain else "dry",
            "view": view,
            "generated_at_utc": GENERATED_AT,
            "results": rows,
        }
    )


def _build_refreshed_prediction_payload(selected_track: str, mode: str, rain: bool) -> dict[str, object]:
    scripts_dir = PROJECT_ROOT / "scripts"
    if not scripts_dir.exists():
        raise RuntimeError(
            "Prediction refresh is unavailable because the generation scripts are not deployed."
        )

    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    from scripts.build_vercel_predictions import probability_rows, ranking_rows

    rain_key = "1" if rain else "0"
    rain_value = 1 if rain else 0
    payload = deepcopy(PREDICTION_DATA)
    payload["generated_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    payload["predictions"][mode][rain_key][selected_track] = {
        "ranking": ranking_rows(selected_track, mode, rain_value),
        "probabilities": probability_rows(selected_track, mode, rain_value),
    }
    return payload


def _persist_prediction_data(payload: dict[str, object]) -> None:
    try:
        PREDICTION_PATH.write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
            newline="\n",
        )
    except OSError:
        if os.environ.get("VERCEL"):
            return
        raise


_apply_prediction_data(_load_prediction_data())


def _request_state() -> tuple[str, str, bool, str, bool]:
    selected_track = request.args.get("track", DEFAULT_TRACK)
    if selected_track not in TRACK_SET:
        selected_track = DEFAULT_TRACK

    mode = request.args.get("mode", "qualifying")
    if mode not in MODE_LABELS:
        mode = "qualifying"

    view = request.args.get("view", "ranking")
    if view not in VIEW_LABELS:
        view = "ranking"

    rain = request.args.get("rain") == "1"
    submitted = True
    return selected_track, mode, rain, view, submitted


def _prediction_rows(selected_track: str, mode: str, rain: bool, view: str) -> list[dict[str, object]]:
    rain_key = "1" if rain else "0"
    predictions = PREDICTION_DATA["predictions"]
    try:
        rows = predictions[mode][rain_key][selected_track][view]
    except KeyError:
        return []
    return [dict(row) for row in rows]


def _frontend_index():
    index_path = WEB_DIST / "index.html"
    if not index_path.exists():
        return (
            jsonify(
                {
                    "error": "Frontend build not found",
                    "hint": "Run `npm run build` from the web directory before deployment.",
                }
            ),
            503,
        )
    return send_file(index_path, max_age=0)


@app.get("/")
def index():
    return _frontend_index()


@app.get("/api/predict")
def predict_api():
    selected_track, mode, rain, view, _ = _request_state()
    return _prediction_response(selected_track, mode, rain, view)


@app.post("/api/refresh")
def refresh_predictions_api():
    selected_track, mode, rain, view, _ = _request_state()

    try:
        with REFRESH_LOCK:
            payload = _build_refreshed_prediction_payload(selected_track, mode, rain)
            _persist_prediction_data(payload)
            _apply_prediction_data(payload)
    except Exception as exc:
        return (
            jsonify(
                {
                    "error": "Prediction refresh failed",
                    "detail": str(exc),
                }
            ),
            503,
        )

    return _prediction_response(selected_track, mode, rain, view)


@app.get("/background.png")
def background():
    image_path = _project_file("image_0.png")
    if not image_path.exists():
        return ("", 404)
    return send_file(image_path, mimetype="image/png", max_age=86400)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/<path:path>")
def frontend_asset(path: str):
    safe_path = safe_join(WEB_DIST, path)
    if safe_path and Path(safe_path).is_file():
        max_age = 31536000 if path.startswith("assets/") else 3600
        return send_from_directory(WEB_DIST, path, max_age=max_age)
    return _frontend_index()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=True)

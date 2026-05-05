from __future__ import annotations

import json
import os
from pathlib import Path

from flask import Flask, jsonify, render_template_string, request, send_file


PROJECT_ROOT = Path(__file__).resolve().parent
PREDICTION_DATA = json.loads((PROJECT_ROOT / "predictions.json").read_text(encoding="utf-8"))


app = Flask(__name__)

TRACK_NAMES = list(PREDICTION_DATA["tracks"])
TRACK_SET = set(TRACK_NAMES)
DEFAULT_TRACK = TRACK_NAMES[0]
TRACK_METADATA = PREDICTION_DATA.get("track_metadata", {})
GENERATED_AT = PREDICTION_DATA.get("generated_at_utc", "unknown")
CALENDAR_LABEL = PREDICTION_DATA.get("calendar", "Official 2026 Formula 1 calendar")
MODE_LABELS = {
    "qualifying": "Qualifying",
    "race": "Race",
}
VIEW_LABELS = {
    "ranking": "Classification",
    "probabilities": "Win probabilities",
}


PAGE_TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>F1 2026 Prediction Center</title>
    <style>
      :root {
        color-scheme: dark;
        --bg: #070809;
        --panel: rgba(12, 15, 18, 0.86);
        --panel-strong: rgba(18, 22, 27, 0.95);
        --line: rgba(255, 255, 255, 0.14);
        --muted: #aeb8c2;
        --text: #f7f8f9;
        --red: #e10600;
        --cyan: #48d1cc;
        --yellow: #ffce44;
      }

      * {
        box-sizing: border-box;
      }

      body {
        min-height: 100vh;
        margin: 0;
        color: var(--text);
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background:
          linear-gradient(90deg, rgba(7, 8, 9, 0.94), rgba(7, 8, 9, 0.72) 46%, rgba(7, 8, 9, 0.86)),
          url("/background.png") center / cover fixed,
          var(--bg);
      }

      main {
        width: min(1180px, calc(100% - 32px));
        min-height: 100vh;
        margin: 0 auto;
        padding: 40px 0;
        display: grid;
        grid-template-rows: auto 1fr;
        gap: 22px;
      }

      header {
        display: flex;
        align-items: end;
        justify-content: space-between;
        gap: 20px;
        padding-bottom: 12px;
        border-bottom: 1px solid var(--line);
      }

      h1 {
        margin: 0;
        max-width: 760px;
        font-size: clamp(2.1rem, 5vw, 4.8rem);
        line-height: 0.92;
        letter-spacing: 0;
      }

      .status {
        min-width: 148px;
        padding: 10px 13px;
        border: 1px solid rgba(72, 209, 204, 0.36);
        background: rgba(72, 209, 204, 0.11);
        color: #dffffd;
        font-size: 0.84rem;
        text-align: center;
        text-transform: uppercase;
      }

      .source {
        margin-top: 8px;
        color: var(--muted);
        font-size: 0.78rem;
        line-height: 1.35;
      }

      .workspace {
        display: grid;
        grid-template-columns: 320px 1fr;
        gap: 18px;
        align-items: start;
      }

      form,
      .results {
        border: 1px solid var(--line);
        background: var(--panel);
        backdrop-filter: blur(18px);
      }

      form {
        padding: 18px;
        display: grid;
        gap: 18px;
        position: sticky;
        top: 24px;
      }

      label,
      .field-title {
        display: block;
        margin-bottom: 8px;
        color: var(--muted);
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }

      select {
        width: 100%;
        min-height: 44px;
        padding: 0 12px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 2px;
        background: rgba(255, 255, 255, 0.08);
        color: var(--text);
        font: inherit;
      }

      .segments {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 6px;
      }

      .segments input {
        position: absolute;
        opacity: 0;
      }

      .segments span {
        display: grid;
        min-height: 40px;
        place-items: center;
        border: 1px solid rgba(255, 255, 255, 0.15);
        background: rgba(255, 255, 255, 0.07);
        color: var(--muted);
        font-size: 0.9rem;
        cursor: pointer;
      }

      .segments input:checked + span {
        border-color: rgba(225, 6, 0, 0.82);
        background: rgba(225, 6, 0, 0.22);
        color: var(--text);
      }

      .toggle {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        margin: 0;
        padding: 12px;
        border: 1px solid rgba(255, 255, 255, 0.14);
        background: rgba(255, 255, 255, 0.06);
        color: var(--text);
        font-size: 0.95rem;
        font-weight: 600;
        letter-spacing: 0;
        text-transform: none;
      }

      .toggle input {
        width: 20px;
        height: 20px;
        accent-color: var(--red);
      }

      .actions {
        display: grid;
        gap: 8px;
      }

      button {
        min-height: 46px;
        border: 0;
        border-radius: 2px;
        background: var(--red);
        color: white;
        font: inherit;
        font-weight: 800;
        cursor: pointer;
      }

      button.secondary {
        border: 1px solid rgba(255, 255, 255, 0.16);
        background: rgba(255, 255, 255, 0.08);
      }

      .results {
        min-height: 516px;
        overflow: hidden;
      }

      .results-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        padding: 18px 20px;
        background: var(--panel-strong);
        border-bottom: 1px solid var(--line);
      }

      h2 {
        margin: 0;
        font-size: 1.25rem;
        letter-spacing: 0;
      }

      .meta {
        color: var(--muted);
        font-size: 0.9rem;
        white-space: nowrap;
      }

      table {
        width: 100%;
        border-collapse: collapse;
      }

      th,
      td {
        padding: 12px 14px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        text-align: left;
      }

      th {
        color: var(--muted);
        font-size: 0.72rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
      }

      td:first-child,
      th:first-child {
        width: 72px;
        text-align: center;
      }

      .score {
        color: #dfe6ed;
        font-variant-numeric: tabular-nums;
      }

      .prob-list {
        display: grid;
        gap: 10px;
        padding: 18px 20px 24px;
      }

      .prob-row {
        display: grid;
        grid-template-columns: 34px minmax(120px, 210px) 1fr 72px;
        gap: 12px;
        align-items: center;
      }

      .rank {
        color: var(--muted);
        text-align: right;
        font-variant-numeric: tabular-nums;
      }

      .driver {
        min-width: 0;
      }

      .driver strong,
      .driver span {
        display: block;
        overflow-wrap: anywhere;
      }

      .driver span {
        color: var(--muted);
        font-size: 0.82rem;
      }

      .bar {
        height: 12px;
        overflow: hidden;
        background: rgba(255, 255, 255, 0.12);
      }

      .bar div {
        height: 100%;
        min-width: 3px;
        background: linear-gradient(90deg, var(--red), var(--yellow), var(--cyan));
      }

      .empty,
      .error {
        min-height: 450px;
        display: grid;
        place-items: center;
        padding: 28px;
        color: var(--muted);
        text-align: center;
      }

      .error {
        color: #ffd9d7;
      }

      @media (max-width: 820px) {
        main {
          width: min(100% - 22px, 640px);
          padding: 22px 0;
        }

        header,
        .results-header {
          align-items: start;
          flex-direction: column;
        }

        .workspace {
          grid-template-columns: 1fr;
        }

        form {
          position: static;
        }

        .meta {
          white-space: normal;
        }

        .prob-row {
          grid-template-columns: 30px 1fr 58px;
        }

        .prob-row .bar {
          grid-column: 2 / 4;
        }

        th:nth-child(3),
        td:nth-child(3) {
          display: none;
        }
      }
    </style>
  </head>
  <body>
    <main>
      <header>
        <h1>F1 2026 Prediction Center</h1>
        <div>
          <div class="status">22-round build</div>
          <div class="source">Updated {{ generated_at }}</div>
        </div>
      </header>

      <section class="workspace">
        <form method="get" action="/">
          <div>
            <label for="track">Grand Prix</label>
            <select id="track" name="track">
              {% for option in tracks %}
                <option value="{{ option }}" {% if option == selected_track %}selected{% endif %}>
                  R{{ track_metadata[option].Round }} - {{ option }}
                </option>
              {% endfor %}
            </select>
          </div>

          <div>
            <div class="field-title">Session</div>
            <div class="segments">
              <label>
                <input type="radio" name="mode" value="qualifying" {% if mode == "qualifying" %}checked{% endif %}>
                <span>Qualifying</span>
              </label>
              <label>
                <input type="radio" name="mode" value="race" {% if mode == "race" %}checked{% endif %}>
                <span>Race</span>
              </label>
            </div>
          </div>

          <label class="toggle">
            Wet session
            <input type="checkbox" name="rain" value="1" {% if rain %}checked{% endif %}>
          </label>

          <div class="actions">
            <button type="submit" name="view" value="ranking">Show classification</button>
            <button class="secondary" type="submit" name="view" value="probabilities">Show win probabilities</button>
          </div>
        </form>

        <section class="results">
          <div class="results-header">
            <h2>{{ heading }}</h2>
            <div class="meta">{{ event }} / {{ mode_label }} / {{ weather }}</div>
          </div>

          {% if error %}
            <div class="error">{{ error }}</div>
          {% elif not submitted %}
            <div class="empty">Select a circuit, session, and output.</div>
          {% elif rows and view == "ranking" %}
            <table>
              <thead>
                <tr>
                  <th>No</th>
                  <th>Driver</th>
                  <th>Team</th>
                  <th>AI score</th>
                </tr>
              </thead>
              <tbody>
                {% for row in rows %}
                  <tr>
                    <td>{{ row.rank }}</td>
                    <td>{{ row.driver }}</td>
                    <td>{{ row.team }}</td>
                    <td class="score">{{ row.score }}</td>
                  </tr>
                {% endfor %}
              </tbody>
            </table>
          {% elif rows %}
            <div class="prob-list">
              {% for row in rows %}
                <div class="prob-row">
                  <div class="rank">{{ row.rank }}</div>
                  <div class="driver">
                    <strong>{{ row.driver }}</strong>
                    <span>{{ row.team }}</span>
                  </div>
                  <div class="bar"><div style="width: {{ row.width }}%"></div></div>
                  <div class="score">{{ row.probability }}%</div>
                </div>
              {% endfor %}
            </div>
          {% else %}
            <div class="empty">No prediction rows were returned.</div>
          {% endif %}
        </section>
      </section>
    </main>
  </body>
</html>
"""


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


@app.get("/")
def index():
    selected_track, mode, rain, view, submitted = _request_state()
    track_info = TRACK_METADATA.get(selected_track, {})
    rows = []
    error = ""

    if submitted:
        try:
            rows = _prediction_rows(selected_track, mode, rain, view)
        except Exception as exc:  # pragma: no cover - surfaced in production UI
            error = f"Prediction failed: {exc}"

    return render_template_string(
        PAGE_TEMPLATE,
        tracks=TRACK_NAMES,
        track_metadata=TRACK_METADATA,
        selected_track=selected_track,
        event=track_info.get("Event", selected_track),
        mode=mode,
        mode_label=MODE_LABELS[mode],
        rain=rain,
        weather="Wet" if rain else "Dry",
        view=view,
        heading=VIEW_LABELS[view],
        rows=rows,
        submitted=submitted,
        error=error,
        generated_at=GENERATED_AT,
        calendar=CALENDAR_LABEL,
    )


@app.get("/api/predict")
def predict_api():
    selected_track, mode, rain, view, _ = _request_state()
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


@app.get("/background.png")
def background():
    image_path = PROJECT_ROOT / "image_0.png"
    if not image_path.exists():
        return ("", 404)
    return send_file(image_path, mimetype="image/png", max_age=86400)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=True)

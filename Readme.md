# F1 2026 Prediction Center

A Streamlit web application that predicts qualifying and race performance for the 2026 Formula 1 season. It uses XGBoost regression models tuned with Optuna and trained on historical FastF1 data spanning the 2022–2025 seasons. Users select a Grand Prix and a weather condition (dry or wet) and the app returns a ranked driver order plus a win-probability distribution.

## Features

- **Qualifying mode** — predicted grid order based on a per-driver performance index.
- **Race mode** — predicted finishing order based on a separate race-pace model.
- **Weather toggle** — dry vs. wet sessions are modelled with different feature inputs.
- **Win probability** — softmax over the model's raw scores, rendered as a Plotly pie chart.
- **22 official 2026 tracks** — sourced from the published 2026 calendar.

## Tech stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ (tested up to 3.14) |
| Web UI | Streamlit, Plotly |
| Data | pandas, NumPy |
| Machine learning | XGBoost, scikit-learn, Optuna |
| F1 data ingestion | FastF1, tqdm |
| Model persistence | joblib |

All dependencies are pinned in [`requirements.txt`](./requirements.txt).

## Project structure

```
F1/
├── code/                      # Qualifying pipeline + Streamlit app
│   ├── app.py                 # Entry point — `streamlit run code/app.py`
│   ├── engine.py              # Qualifying inference
│   ├── engine_race.py         # Race inference
│   ├── probability.py         # Softmax over qualifying scores
│   ├── probability_race.py    # Softmax over race scores
│   ├── driver_team_circuit_constants.py  # 2026 driver/team/track tables
│   ├── collect_qualy_data.py  # FastF1 → raw qualifying CSV
│   ├── merging_raw_datas.py   # Raw qualifying CSVs → master dataset
│   ├── preprocessing.py       # Cleaning + encoding
│   ├── feature_engineering.py # Track-DNA + driver/team features
│   ├── model_training.py      # XGBoost + Optuna training loop
│   └── make_prediction.py     # CLI prediction helper
├── rcode/                     # Race pipeline (mirrors code/ for race data)
├── dataset/                   # Qualifying CSVs (raw → processed → features)
├── rdataset/                  # Race CSVs (same shape)
├── models/                    # Trained .pkl model files + feature-name lists
├── docs/                      # Project documentation, known issues
├── image_0.png                # UI background image
├── requirements.txt           # Pinned Python dependencies
└── Readme.md                  # This file
```

## Local setup

### Prerequisites

- Python 3.11 or newer (3.14 is supported but bleeding-edge — 3.11/3.12 are recommended for stability)
- Git
- ~500 MB free disk space (datasets + cached FastF1 sessions)

### Install

**Windows (PowerShell):**

```powershell
git clone https://github.com/Plammon/F1.git
cd F1
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

**macOS / Linux:**

```bash
git clone https://github.com/Plammon/F1.git
cd F1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run the app

From the repo root, with the virtual environment active:

```bash
streamlit run code/app.py
```

The app opens at <http://localhost:8501>. Pick a Grand Prix in the sidebar, toggle the rain checkbox if needed, choose Qualifying or Race mode, and click the prediction button.

### Re-training the models *(optional)*

The repo ships with pre-trained models in `models/`. To re-train from scratch, run the qualifying pipeline:

```bash
python code/collect_qualy_data.py     # 1. download raw FastF1 sessions
python code/merging_raw_datas.py      # 2. merge yearly CSVs
python code/preprocessing.py          # 3. clean + encode
python code/feature_engineering.py    # 4. add engineered features
python code/model_training.py         # 5. train + save .pkl with Optuna tuning
```

The race pipeline lives in `rcode/` and follows the same five steps with `_race` suffixes.

> The first run will download several seasons of FastF1 telemetry into a local cache directory (`.f1_cache_qualy/` / `.f1_cache_race/`). These directories are git-ignored and may grow to a few hundred MB.

## Configuration & secrets

The application does not require any external API keys or credentials at the moment, but the project follows a standard 12-factor pattern in case any are added later:

- A tracked template file [`.env.example`](./.env.example) documents every environment variable the app understands, with placeholder values only.
- Real values live in a local `.env` file which is listed in `.gitignore` and must never be committed.
- For Streamlit-specific secrets, the convention is to use `.streamlit/secrets.toml` — that path is also git-ignored.
- In production (Streamlit Community Cloud, Render, etc.) values are set through the platform's environment-variable UI, never shipped in the repository.

To get started locally:

```bash
cp .env.example .env        # macOS / Linux
Copy-Item .env.example .env # PowerShell
```

then edit `.env` with whatever overrides you need.

## Deployment

> **Live URL:** *to be added once the application is deployed.*

Deployment is documented in [`docs/`](./docs/) (forthcoming).

## Known issues & technical debt

Tracked in [`docs/KNOWN_ISSUES.md`](./docs/KNOWN_ISSUES.md). The most visible item today is the XGBoost pickle-format compatibility warning when loading older `.pkl` models — predictions are correct, only the logs are noisy.

## Team

| Name | Role |
|---|---|
| Eren ÖZŞAHİN |  |
| Furkan UKUŞ |  |
| Baran KARLUK |  |
| Barış AYDIN |  |
| Yusuf KORKMAZ |  |

*(Roles to be filled in when team contributions are finalised for the §1.10 section of the final report.)*

## Data & acknowledgements

- Race and qualifying telemetry are obtained via [FastF1](https://github.com/theOehrly/Fast-F1), an open-source Python package that wraps the official Formula 1 timing data.
- F1 team names, driver line-ups, and the 2026 race calendar are taken from publicly available sources for educational use only.
- This is an academic project for the **Fundamentals of Software Engineering** course; it is not affiliated with Formula 1, FIA, or any constructor.

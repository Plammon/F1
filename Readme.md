# F1 2026 Prediction Center

A Streamlit application that predicts qualifying and race performance for the 2026 Formula 1 season. It uses trained XGBoost models, historical FastF1-derived data from 2022-2025, and a 2026 driver/circuit scenario layer. Users select a Grand Prix, session type, and dry/wet condition; the app returns a ranked driver order and a win-probability distribution.

## Features

- Qualifying mode: predicted grid order based on a per-driver performance index.
- Race mode: predicted finishing order based on a race-pace model plus engineered race scenario features.
- Weather toggle: dry and wet sessions adjust rain, track temperature, and driver track/weather form inputs.
- Win probability: softmax over the prediction scores, rendered as a Plotly pie chart in Streamlit.
- Official 2026 calendar scope: 22 rounds from the published Formula 1 2026 calendar.

## Runtime And Deployment

The source-of-truth application runtime is Streamlit:

```bash
streamlit run code/app.py
```

The public Vercel URL is a size-safe deployment adapter for the same product. Vercel's Python functions are not a good fit for a long-running Streamlit websocket server, and the project must stay below Vercel's 500 MB deployment limit. To keep the public URL reliable and small, `scripts/build_vercel_predictions.py` runs the trained models ahead of deployment and writes `predictions.json`; `vercel_app.py` serves that payload through a lightweight Flask UI and JSON API.

Public URL: https://f1-alpha-jet.vercel.app

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Primary web UI | Streamlit, Plotly |
| Vercel public adapter | Flask, precomputed JSON |
| Data | pandas, NumPy |
| Machine learning | XGBoost, scikit-learn, Optuna |
| F1 data ingestion | FastF1, tqdm |
| Model persistence | joblib |

Dependencies for the full Streamlit/model runtime are listed in `requirements.txt`. The Vercel adapter uses `pyproject.toml` and intentionally installs only the small dependencies needed by the public deployment.

## Project Structure

```text
F1/
├── code/                       # Streamlit app, qualifying engine, shared constants
├── rcode/                      # Race data and model pipeline
├── dataset/                    # Qualifying CSV data
├── rdataset/                   # Race CSV data
├── models/                     # Trained model files and feature-name lists
├── scripts/                    # Vercel prediction-payload builder
├── api/index.py                # Vercel function entrypoint
├── vercel_app.py               # Lightweight Vercel UI/API adapter
├── predictions.json            # Generated deployment payload
├── image_0.png                 # UI background image
├── requirements.txt            # Full Streamlit/model runtime dependencies
├── pyproject.toml              # Vercel adapter dependencies
└── vercel.json                 # Vercel routing config
```

## Local Setup

```powershell
git clone https://github.com/Plammon/F1.git
cd F1
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
streamlit run code/app.py
```

The app opens at http://localhost:8501.

## Rebuilding The Vercel Payload

After changing model logic, calendar constants, or datasets:

```powershell
python scripts/build_vercel_predictions.py
python scripts/verify_prediction_payload.py
```

This regenerates `predictions.json` from the same prediction modules used by Streamlit. The deployed package remains small because `.vercelignore` includes only the Flask adapter, generated JSON payload, background image, and Vercel config.

## Models And Calendar Mapping

The user-facing app shows circuit names such as `Albert Park`, `COTA`, and `Yas Marina`. The saved qualifying and race models were trained with different GP labels in several places, so `code/driver_team_circuit_constants.py` stores model aliases for each circuit. This prevents one-hot GP features from being zero-filled during inference.

Madrid is new for the 2026 calendar, so it uses the historical Spanish GP as the nearest GP proxy while retaining a distinct track type and race scenario profile.

## Configuration And Secrets

No external API keys or secrets are required. `.env.example` documents the current convention for future environment variables. Real `.env` files and Streamlit secrets are git-ignored and should not be committed.

## Known Issues And Technical Debt

Tracked in `docs/KNOWN_ISSUES.md`.

## Team

| Name | Role |
|---|---|
| Eren Ozsahin |  |
| Furkan Ukus |  |
| Baran Karluk |  |
| Baris Aydin |  |
| Yusuf Korkmaz |  |

## Acknowledgements

Race and qualifying data are obtained via FastF1. This is an academic project for the Fundamentals of Software Engineering course and is not affiliated with Formula 1, FIA, or any constructor.

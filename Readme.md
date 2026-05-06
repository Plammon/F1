# F1 2026 Prediction Center

F1 2026 Prediction Center is an academic web application for predicting Formula 1 qualifying and race outcomes across the 2026 calendar. Users select a Grand Prix, session type, weather condition, and output view, then the deployed site returns either a predicted classification or a win-probability ranking.

Public deployment: https://f1-alpha-jet.vercel.app

Repository: https://github.com/ysfkrkmz35/F1

## Website Features

- Desktop-focused prediction dashboard for live demo use.
- 2026 calendar selector covering 22 Formula 1 rounds.
- Qualifying and race prediction modes.
- Dry and wet weather scenarios.
- Classification and win-probability views.
- Public Vercel deployment backed by precomputed prediction data.
- Health endpoint at `/health` and JSON prediction endpoint at `/api/predict`.

## Website Tech Stack

| Layer | Technology |
|---|---|
| Public frontend | React 19, Vite |
| Public API adapter | Flask on Vercel Python Functions |
| Deployment payload | `predictions.json` precomputed from the trained models |
| Source model runtime | Python, pandas, NumPy, scikit-learn, XGBoost |
| Local full app runtime | Streamlit, Plotly |
| Deployment platform | Vercel |

The full Streamlit/model runtime remains in `requirements.txt`. The Vercel website runtime intentionally uses the minimal `pyproject.toml` dependency set so the serverless deployment stays below Vercel's function size limit.

## Project Structure

```text
F1/
|-- api/index.py                 # Vercel function entrypoint
|-- vercel_app.py                # Flask adapter serving the public website and API
|-- vercel.json                  # Vercel routing and function config
|-- pyproject.toml               # Minimal Vercel website dependencies
|-- predictions.json             # Generated prediction payload used by the public site
|-- image_0.png                  # Website background image
|-- web/
|   |-- src/                     # React dashboard source
|   |-- dist/                    # Built Vite assets served in production
|   |-- package.json             # Frontend scripts and dependencies
|-- code/                        # Streamlit app and qualifying prediction engine
|-- rcode/                       # Race data and model pipeline
|-- dataset/                     # Qualifying CSV data
|-- rdataset/                    # Race CSV data
|-- models/                      # Trained model files and feature-name lists
|-- scripts/                     # Prediction payload generation and verification scripts
|-- docs/KNOWN_ISSUES.md         # Technical debt appendix for the final report
|-- Dockerfile                   # Container definition for the full Streamlit app
|-- docker-compose.yml           # Local container orchestration file
|-- requirements.txt             # Full Streamlit/model runtime dependencies
```

## Local Setup

Install the full Python runtime when you need to run the Streamlit version or rebuild model outputs:

```powershell
git clone https://github.com/ysfkrkmz35/F1.git
cd F1
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
streamlit run code/app.py
```

The Streamlit app opens at http://localhost:8501.

## Frontend Development

The public Vercel website uses the React/Vite app in `web/`.

```powershell
cd web
npm install
npm run dev
```

Before deployment, rebuild the static assets that Flask serves from `web/dist`:

```powershell
cd web
npm run build
```

## Rebuilding The Vercel Prediction Payload

After changing model logic, calendar constants, or datasets:

```powershell
python scripts/build_vercel_predictions.py
python scripts/verify_prediction_payload.py
```

This regenerates `predictions.json`, which is the data source used by the public website. The deployed Vercel package includes only the Flask adapter, generated JSON payload, background image, routing config, and built Vite assets; it does not ship the full model files or training datasets.

## Deployment

The deployed website is reachable at:

https://f1-alpha-jet.vercel.app

Vercel is used because the final assignment requires a public URL for the live demo and the project already fits a request/response deployment model when predictions are precomputed. The production deployment serves:

- `/` for the React dashboard.
- `/api/predict` for prediction data.
- `/health` for deployment health checks.
- `/background.png` for the dashboard image.

No secrets are required for the public demo. Real environment files are ignored by Git; `.env.example` documents the convention for future configuration.

## Demo Walkthrough

For the final assignment live demo, open the public URL and walk through this website user story:

1. Select a Grand Prix from the 2026 calendar.
2. Switch between Qualifying and Race.
3. Toggle Dry and Wet weather.
4. Compare Classification and Win Probability views.
5. Explain that the public site is served from Vercel using precomputed model outputs in `predictions.json`.

## Quality And Technical Debt

Known website and deployment tradeoffs are tracked in `docs/KNOWN_ISSUES.md`. The most important deployment tradeoff is that Vercel serves a generated web adapter rather than the long-running Streamlit websocket server.

## Team

| Name | Contribution area |
|---|---|
| Eren Ozsahin | Project implementation and final demo support |
| Furkan Ukus | Project implementation and final demo support |
| Baran Karluk | Project implementation and final demo support |
| Baris Aydin | Project implementation and final demo support |
| Yusuf Korkmaz | Project implementation, web deployment, and final demo support |

## Acknowledgements

Race and qualifying data are obtained via FastF1. This is an academic project for the Fundamentals of Software Engineering course and is not affiliated with Formula 1, FIA, or any constructor.

# Known Issues & Technical Debt

This file feeds the §1.7 "Known Issues & Technical Debt" appendix of the final report. Each entry: what, why deferred, how to fix.

---

## TD-001 — XGBoost model pickle compatibility warnings

**Symptom.** When `engine.py`, `engine_race.py`, `probability.py`, or `probability_race.py` calls `joblib.load(...)` on the `.pkl` files in `models/`, XGBoost prints a `UserWarning` recommending the model be re-saved via `Booster.save_model`.

**Why it happens.** The model files were trained and pickled with an older XGBoost version. We are now running XGBoost 2.1.x. Pickle works across minor versions but XGBoost upstream warns that long-term compatibility is not guaranteed and prefers its own `save_model`/`load_model` (JSON/UBJ) format.

**Why deferred.** Predictions still produce correct output; this is a logging/forward-compatibility issue, not a correctness one. Re-saving requires re-running the training scripts (`code/model_training.py`, `rcode/model_training_race.py`) which need the full training dataset and Optuna tuning runs — too costly for the final-week timeline.

**How to fix later.**
1. Re-run training (or write a one-off script that loads each `.pkl` and re-saves the underlying booster):
   ```python
   model = joblib.load("models/f1_optuna_pi_model.pkl")
   model.get_booster().save_model("models/f1_optuna_pi_model.json")
   ```
2. Update the four loader modules to use `xgb.Booster(); booster.load_model("...json")` instead of `joblib.load`.
3. Drop the `.pkl` files.

**Logged.** 2026-05-05, during local smoke test of `requirements.txt`.

---

## TD-002 — Dockerfile / docker-compose.yml not yet smoke-tested locally

**Symptom.** `Dockerfile`, `.dockerignore`, and `docker-compose.yml` were authored but never exercised with `docker compose build` / `docker compose up` on a local machine, because no team member's primary dev box has Docker Desktop installed yet.

**Why it happens.** Adding Docker Desktop on Windows pulls in WSL2, requires Windows feature toggles, and at least one reboot — too much friction during the final week. Streamlit Community Cloud (our deploy target) does not need Docker, so the lack of a local container test does not block deployment.

**Why deferred.** The Dockerfile is built from conventional, documented patterns: `python:3.11-slim` base, `libgomp1` for XGBoost, non-root `appuser`, Streamlit's official `STREAMLIT_SERVER_*` environment variables, and a HEALTHCHECK against the documented `/_stcore/health` endpoint. The probability of a syntactic or runtime error is low, but is non-zero until verified.

**How to fix later.**
1. On any machine with Docker installed, from the repo root:
   ```bash
   docker compose build
   docker compose up
   curl http://localhost:8501/_stcore/health   # expect: ok
   ```
2. If anything fails, fix and push.
3. Recommended to do this at least 24 hours before the live demo so there is time to react.

**Logged.** 2026-05-05, while bundling Improvement #4.

---

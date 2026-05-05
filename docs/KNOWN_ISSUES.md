# Known Issues And Technical Debt

This file feeds the final report's "Known Issues and Technical Debt" appendix. Each entry states what remains, why it was deferred, and how to fix it.

---

## TD-001 - XGBoost model pickle compatibility warnings

**Symptom.** Loading the `.pkl` model files can print an XGBoost warning recommending the native `save_model` / `load_model` format.

**Why it happens.** The models were persisted with `joblib`. XGBoost supports this in the short term, but its native JSON/UBJ model format is safer across future XGBoost versions.

**Why deferred.** The models still load and predict correctly. Re-saving or retraining all models is lower priority than keeping the final demo stable.

**How to fix later.**

1. Re-save the trained boosters with `model.get_booster().save_model("model.json")`.
2. Update the loaders to use `xgb.Booster().load_model(...)`.
3. Remove the old `.pkl` files once the new format is verified.

---

## TD-002 - Docker image not yet smoke-tested on a Docker host

**Symptom.** `Dockerfile` and `docker-compose.yml` exist, but they still need a full build/run smoke test on a machine with Docker Desktop or Docker Engine installed.

**Why it happens.** The active development machine did not have Docker ready during the final integration window.

**Why deferred.** The public deployment uses Vercel, and the local Streamlit runtime can be tested directly with `streamlit run code/app.py`.

**How to fix later.**

```bash
docker compose build
docker compose up
curl http://localhost:8501/_stcore/health
```

---

## TD-003 - Vercel deployment is a generated web adapter, not the Streamlit websocket server

**Symptom.** The primary local app runtime is Streamlit, but the public Vercel URL serves a React/Vite dashboard through a lightweight Flask adapter backed by `predictions.json`.

**Why it happens.** Vercel Python functions are optimized for request/response serverless handlers, while Streamlit expects a long-running Tornado/websocket process. The project also needs to stay below Vercel's 500 MB function size limit, so the public website ships precomputed prediction data instead of model files and training datasets.

**Why deferred.** The adapter keeps the public demo URL reliable, small, and aligned with the same prediction engine used by Streamlit. It avoids shipping the full data/model runtime into the Vercel function bundle.

**How to fix later.** Move the public Streamlit runtime to a platform designed for long-running Python web apps, such as Streamlit Community Cloud, Render, Fly.io, or a container host, then keep Vercel only as a redirect if the course still requires that URL.

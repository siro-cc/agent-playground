# Repository Notes

- This is a minimal FastAPI app managed with `uv`.
- Use `uv sync` to install dependencies and create/update `.venv`.
- Run the app with `uv run uvicorn app.main:app --reload`.
- `./start.sh` is the repo-local startup script; it runs `uv sync` first, then starts `uvicorn`, with optional `HOST`, `PORT`, and `RELOAD` overrides.
- The API entrypoint is `app/main.py` and the FastAPI app object is `app`.
- `app/main.py` exposes `GET /health` for liveness and `GET /ready` for readiness.
- Runtime configuration is loaded from the repo-root `.env` file via `app/config.py`.
- `pyproject.toml` sets `[tool.uv].package = false`, so `uv` should run the app directly instead of trying to install a local package.

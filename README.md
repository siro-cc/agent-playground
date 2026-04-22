# agent-playground

Minimal FastAPI project managed with `uv`.

## Configuration

The app loads configuration from `.env`.

Example:

```bash
cp .env.example .env
```

## Run

```bash
uv sync
uv run uvicorn app.main:app --reload
```

Or use the startup script:

```bash
./start.sh
```

Optional overrides:

```bash
HOST=0.0.0.0 PORT=9000 RELOAD=false ./start.sh
```

## Endpoints

- `GET /health`: liveness probe
- `GET /ready`: readiness probe
- `POST /chat`: returns the fixed chat status message

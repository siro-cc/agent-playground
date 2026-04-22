#!/usr/bin/env bash

set -euo pipefail

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"
RELOAD="${RELOAD:-true}"

uv sync

if [ "$RELOAD" = "true" ]; then
    exec uv run uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
fi

exec uv run uvicorn app.main:app --host "$HOST" --port "$PORT"

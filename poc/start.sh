#!/usr/bin/env bash
# Usage:
#   ./start.sh
#   MLFLOW_ENABLED=true DATABRICKS_HOST=... DATABRICKS_TOKEN=... ./start.sh

set -euo pipefail

export MLFLOW_ENABLED="${MLFLOW_ENABLED:-false}"
PORT="${PORT:-8001}"
HOST="${HOST:-127.0.0.1}"

echo "MLflow: $MLFLOW_ENABLED  →  http://${HOST}:${PORT}  (docs: /docs)"

exec uvicorn main:app --host "$HOST" --port "$PORT" --reload

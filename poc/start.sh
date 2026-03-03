#!/usr/bin/env bash
# Start the MLflow Chat POC server.
#
# Usage:
#   ./start.sh               # MLflow OFF (default)
#   MLFLOW_ENABLED=true ./start.sh
#
# MLflow env vars (only needed when MLFLOW_ENABLED=true):
#   DATABRICKS_HOST     e.g. https://your-workspace.azuredatabricks.net
#   DATABRICKS_TOKEN    personal access token
#   MLFLOW_EXPERIMENT_NAME  (default: /Shared/chat-poc)

set -euo pipefail

PORT="${PORT:-8001}"
HOST="${HOST:-127.0.0.1}"
MLFLOW_ENABLED="${MLFLOW_ENABLED:-false}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Dependency check ──────────────────────────────────────────────────────────
if ! python3 -c "import fastapi, uvicorn" 2>/dev/null; then
  echo "Installing dependencies..."
  pip install -q --break-system-packages -r requirements.txt
fi

if [[ "$MLFLOW_ENABLED" == "true" ]]; then
  if ! python3 -c "import mlflow" 2>/dev/null; then
    echo "Installing mlflow[databricks]..."
    pip install -q --break-system-packages "mlflow[databricks]>=3.1"
  fi
  if [[ -z "${DATABRICKS_HOST:-}" ]]; then
    echo "ERROR: DATABRICKS_HOST must be set when MLFLOW_ENABLED=true" >&2
    exit 1
  fi
  if [[ -z "${DATABRICKS_TOKEN:-}" ]]; then
    echo "ERROR: DATABRICKS_TOKEN must be set when MLFLOW_ENABLED=true" >&2
    exit 1
  fi
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "  MLflow Chat POC"
echo "  ───────────────────────────────────────"
echo "  URL:     http://${HOST}:${PORT}"
echo "  Docs:    http://${HOST}:${PORT}/docs"
echo "  MLflow:  ${MLFLOW_ENABLED}"
if [[ "$MLFLOW_ENABLED" == "true" ]]; then
  echo "  Host:    ${DATABRICKS_HOST}"
  echo "  Exp:     ${MLFLOW_EXPERIMENT_NAME:-/Shared/chat-poc}"
fi
echo "  ───────────────────────────────────────"
echo ""

export MLFLOW_ENABLED

uvicorn_bin="$(python3 -m site --user-base)/bin/uvicorn"
if ! command -v uvicorn &>/dev/null && [[ -x "$uvicorn_bin" ]]; then
  exec "$uvicorn_bin" main:app --host "$HOST" --port "$PORT" --reload
else
  exec uvicorn main:app --host "$HOST" --port "$PORT" --reload
fi

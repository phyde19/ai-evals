.DEFAULT_GOAL := help
PORT ?= 8001
HOST ?= 127.0.0.1

.PHONY: help start start-mlflow install lint

help:
	@echo ""
	@echo "  MLflow Chat POC"
	@echo ""
	@echo "  make start          Start app with MLflow OFF (mock UUIDs)"
	@echo "  make start-mlflow   Start app with MLflow ON  (requires env vars)"
	@echo "  make install        Install Python dependencies"
	@echo ""
	@echo "  Required env vars for start-mlflow:"
	@echo "    DATABRICKS_HOST=https://your-workspace.azuredatabricks.net"
	@echo "    DATABRICKS_TOKEN=<pat>"
	@echo "    MLFLOW_EXPERIMENT_NAME=/Shared/chat-poc  (optional)"
	@echo ""

install:
	pip install -q --break-system-packages -r requirements.txt

start: install
	PORT=$(PORT) HOST=$(HOST) MLFLOW_ENABLED=false bash start.sh

start-mlflow: install
	@if [ -z "$$DATABRICKS_HOST" ]; then \
		echo "ERROR: DATABRICKS_HOST is not set"; exit 1; fi
	@if [ -z "$$DATABRICKS_TOKEN" ]; then \
		echo "ERROR: DATABRICKS_TOKEN is not set"; exit 1; fi
	PORT=$(PORT) HOST=$(HOST) MLFLOW_ENABLED=true bash start.sh

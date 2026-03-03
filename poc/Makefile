.DEFAULT_GOAL := help
PORT ?= 8001
HOST ?= 127.0.0.1

.PHONY: help start start-mlflow

help:
	@echo "make start          MLflow OFF"
	@echo "make start-mlflow   MLflow ON  (requires DATABRICKS_HOST, DATABRICKS_TOKEN)"

start:
	PORT=$(PORT) HOST=$(HOST) bash start.sh

start-mlflow:
	PORT=$(PORT) HOST=$(HOST) MLFLOW_ENABLED=true bash start.sh

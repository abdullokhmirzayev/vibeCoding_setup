.PHONY: help setup test run-cli run-api docker-up docker-down clean

help:
	@echo "Available commands:"
	@echo "  make setup      - Create .venv and install all dependencies"
	@echo "  make test       - Run all unit tests with pytest"
	@echo "  make run-cli    - Run interactive CLI console"
	@echo "  make run-api    - Launch FastAPI REST API server (http://localhost:8000)"
	@echo "  make docker-up  - Launch local Qdrant, Postgres, and Langfuse"
	@echo "  make docker-down- Stop local docker services"
	@echo "  make clean      - Remove caches and temporary logs"

setup:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt

test:
	.venv/bin/pytest tests/ -v

run-cli:
	.venv/bin/python -m src.cli --help

run-api:
	.venv/bin/uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload

docker-up:
	docker compose up -d

docker-down:
	docker compose down

clean:
	rm -rf __pycache__ .pytest_cache .logs/*.jsonl .memory.db

.PHONY: help dev test sync up down status logs clean

help:
	@echo "FastKanban - Convenience Commands"
	@echo "  make dev    - Run development server locally with auto-reload"
	@echo "  make test   - Run automated pytest suite"
	@echo "  make sync   - Sync dependencies via uv"
	@echo "  make up     - Launch Docker Compose containers in background"
	@echo "  make down   - Stop Docker Compose containers"
	@echo "  make status - Check Docker Compose service and health status"
	@echo "  make logs   - Follow Docker Compose logs"

dev:
	uv run uvicorn app.main:app --reload --port 8000

test:
	uv run pytest

sync:
	uv sync

up:
	docker compose up --build -d

down:
	docker compose down

status:
	docker compose ps

logs:
	docker compose logs -f


.PHONY: up down build logs shell test lint fmt migrate revision

up:
	docker compose up --build

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f backend

shell:
	docker compose exec backend bash

test:
	docker compose exec backend pytest -v

lint:
	docker compose exec backend ruff check .

fmt:
	docker compose exec backend ruff format .

migrate:
	docker compose exec backend alembic upgrade head

revision:
	docker compose exec backend alembic revision --autogenerate -m "$(m)"
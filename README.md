
# KnowledgePilot AI — Backend

## Quick start

    cp .env.example .env      # edit JWT_SECRET_KEY at minimum
    make up

Then visit:
- http://localhost:8000/docs        → Swagger UI
- http://localhost:8000/api/v1/health
- http://localhost:8000/api/v1/ready

## Common commands
- `make up` / `make down` — start/stop the stack
- `make shell` — shell into the backend container
- `make test` — run pytest
- `make lint` / `make fmt` — ruff check / ruff format
- `make migrate` — apply Alembic migrations
- `make revision m="add users table"` — generate a new migration

## Architecture
Clean Architecture, dependency direction inward:

    presentation → application → domain
    infrastructure → implements domain/application interfaces

`domain` never imports from `infrastructure`. AI providers, DB, and storage
are all "infrastructure" — swappable without touching business logic.
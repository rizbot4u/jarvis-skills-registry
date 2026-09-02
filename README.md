# Jarvis AI COO Skill Registry

Multi-tenant backend prototype for the Jarvis AI COO developer evaluation. Organizations can create, review, and activate custom AI skills with strict tenant isolation, immutable versioning, and full audit logging.

## Tech Stack
- FastAPI
- SQLAlchemy
- SQLite (see Architecture Decisions for reasoning)
- Pytest

## Setup

### Option 1 — Local (Python)
pip install -r requirements.txt
uvicorn app.main:app --reload

API docs available at: http://127.0.0.1:8000/docs

### Option 2 — Docker Compose
docker compose up --build

See "Note on Docker Compose" below for a known limitation regarding local verification.

## Running Tests
pytest -v

Expected: 10/10 tests passing.

## Environment Variables
Copy .env.example to .env and fill in real values. No secrets are committed to this repo.

## API Examples

Create an organization:
curl -X 'POST' 'http://127.0.0.1:8000/organizations' -H 'Content-Type: application/json' -d '{"name": "ABC Construction", "description": "Fixture org"}'

Create a skill draft:
curl -X 'POST' 'http://127.0.0.1:8000/skills' -H 'X-Organization-ID: 1' -H 'Content-Type: application/json' -d '{"name": "Invoice Approval Skill", "description": "Automates invoice review"}'

Create a new version:
curl -X 'POST' 'http://127.0.0.1:8000/skills/1/versions' -H 'X-Organization-ID: 1' -H 'Content-Type: application/json' -d '{"version_number": 0, "configuration": "some-config", "created_by": "owner"}'

Activate a version (owner only):
curl -X 'POST' 'http://127.0.0.1:8000/skills/1/activate?version_id=1&actor=owner' -H 'X-Organization-ID: 1'

List active skills:
curl -X 'GET' 'http://127.0.0.1:8000/skills/active' -H 'X-Organization-ID: 1'

Disable a skill:
curl -X 'DELETE' 'http://127.0.0.1:8000/skills/1' -H 'X-Organization-ID: 1'

## Architecture Decisions
See ARCHITECTURE.md in this repo.

## Known Limitations
- Authorization is simulated via an X-Organization-ID header and an actor field rather than real session/JWT-based authentication.
- SQLite is used for local development and portability; PostgreSQL is recommended for production.
- Database schema is auto-created by SQLAlchemy on startup rather than managed via a separate migration tool.
- No pagination or filtering implemented on list endpoints.

## What I Would Implement Next
- Real authentication (JWT or session-based)
- Alembic migrations for schema versioning
- PostgreSQL as the default datastore
- Pagination and filtering on list endpoints
- Role-based permissions beyond a single owner flag

## Note on Docker Compose
Dockerfile and docker-compose.yml are included and believed correct based on the application's dependencies. They were not fully verified to run in this development environment due to a broken system package repository (ChromeOS/Crostini cros-packages signing key issue unrelated to this project) preventing local Docker installation. The application has been fully verified via direct uvicorn execution and pytest, both documented above with real output.

## AI Tools Used
Used AI as a pair-programming aid for scaffolding FastAPI routes, SQLAlchemy models, and test cases. All architecture decisions, testing strategy, and debugging were done and understood by the author, verified by manually re-tracing the full workflow through the Swagger UI.

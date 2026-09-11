# AI Skill Registry — Organization-Scoped Vertical Slice

Multi-tenant backend prototype for managing and executing custom AI "skills" with strict organization-level isolation, immutable versioning, and full audit logging.

[![Tests](https://img.shields.io/badge/tests-10%2F10-brightgreen)]()

---

## Overview

This is a FastAPI backend where multiple organizations can create, review, and activate custom AI skills while preserving strict tenant isolation. Organization A cannot read, modify, or activate Organization B's data — enforced at the ORM query layer via `organization_id` on every request.

## Quick Start

```bash
git clone <repo-url>
cd jarvis-skills-registry
pip install -r requirements.txt
python seed_users.py
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs` for the full Swagger UI.

**Seeded test users** (from `seed_users.py`):
- `owner1` / `password123` — organization 1, owner role
- `user1` / `password123` — organization 1, user role
- `owner2` / `password123` — organization 2, owner role

## Get a Token

```bash
curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=owner1&password=password123"
```

## Core Capabilities

- ✅ Create/list/read skills, scoped to organization
- ✅ Immutable skill versioning — active skills can't be edited in place; changes create a new version
- ✅ Owner-only activation
- ✅ JSON Schema validation on skill execution
- ✅ Full audit logging (org, actor, event, version)
- ✅ JWT auth (OAuth2 password flow) with tenant context carried in token claims

## LLM Agent Orchestrator

`POST /agent/run` demonstrates how registered skills can be exposed to an LLM as callable tools:
1. Fetches the caller's active skills
2. Formats them as LLM-compatible function definitions
3. Executes the selected tool through the same validated execution pipeline

This is a **local proof-of-concept** — it does not call any external LLM API.

### Example

```json
POST /agent/run
{
  "prompt": "Approve invoice #12345",
  "payload": {
    "skill_id": 1,
    "arguments": { "invoice_id": 12345, "amount": 250.0 }
  }
}
```

```json
{
  "prompt": "Approve invoice #12345",
  "selected_skill_id": 1,
  "execution_response": {
    "skill": "Invoice Approver",
    "status": "executed",
    "result": "Skill executed with validation",
    "input": { "invoice_id": 12345, "amount": 250.0 },
    "executed_by": "owner1",
    "organization_id": 1,
    "version": 1
  }
}
```

## Tests

```bash
pytest -v
```

10/10 passing, covering: same-org access, cross-org read/update denial, non-owner activation denial, draft/disabled skill exclusion, version immutability, idempotent activation, invalid-payload rejection, and audit record correctness.

## Architecture Decisions

See `ARCHITECTURE.md`.

## Known Limitations

- SQLite used for local development/portability; PostgreSQL recommended for production
- No pagination/filtering on list endpoints yet
- Schema is auto-created via SQLAlchemy metadata rather than Alembic migrations
- `/agent/run` uses a mock tool-selection payload, not a live LLM call

## What I'd Implement Next

- Alembic migrations for schema versioning
- PostgreSQL as the default datastore
- Live LLM integration (OpenAI/Gemini) for automatic tool selection
- Pagination and filtering on list endpoints

## AI Tools Used

AI was used as a pair-programming aid for route scaffolding, model definitions, and test fixtures. All security logic, tenant-isolation boundaries, and debugging were manually verified and traced through the Swagger UI.

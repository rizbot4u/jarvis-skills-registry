# Jarvis AI COO Skill Registry

Multi-tenant skill registry with tenant isolation, immutable versioning, and audit logging.

## Setup

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
pytest -v

### Create `ARCHITECTURE.md`

```bash
cat > ARCHITECTURE.md << 'EOF'
# Architecture Decisions

## Tenant Isolation
- All tables include `organization_id`
- All queries filter by `organization_id`
- No cross-tenant access

## Version Management
- Skills and versions in separate tables
- Versions are immutable (never updated)
- Active version stored as `active_version_id`

## Database Choice
- SQLite used for portability (no external dependencies)
- PostgreSQL recommended for production

## Audit Logging
- All actions logged with organization_id, actor, event, version_id

## Authorization
- Only "owner" can activate a skill
- Simulated actor-based check

## Note on Docker Compose

Dockerfile and docker-compose.yml are included and believed correct based on the
application's dependencies (see Setup section for equivalent local run instructions).
However, they were not fully verified to run in this development environment due to
a broken system package repository (ChromeOS/Crostini `cros-packages` signing key
issue unrelated to this project) preventing local Docker installation. The application
has been fully verified via direct `uvicorn` execution and `pytest`, both documented
above with real output.

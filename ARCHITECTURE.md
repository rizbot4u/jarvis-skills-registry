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

## Authorization
- Only "owner" can activate a skill
- Simulated actor-based check

## Audit Logging
- All actions logged with organization_id, actor, event, version_id

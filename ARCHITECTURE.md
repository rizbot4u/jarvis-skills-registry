# Architecture

## System Overview

Jarvis is the orchestration and permission layer. It never holds
credentials. All authenticated execution is delegated to a separate
service (Nova Bridge) that holds the secrets.

    ┌──────────────────────┐
    │  LLM Client          │
    │  (Cursor Agent, etc.)│
    └──────────┬───────────┘
               │ MCP (stdio)
               ▼
    ┌──────────────────────┐
    │  jarvis-registry MCP │   mcp_server.py — MCP SDK v2
    │  (this repo)         │   exposes skills as MCP tools
    └──────────┬───────────┘
               │ HTTP + JWT
               ▼
    ┌──────────────────────┐
    │  Jarvis FastAPI      │   app/main.py — port 8000
    │  (this repo)         │   auth, registry, orchestrator
    └──────────┬───────────┘
               │ HTTP POST (only if skill config has
               │            bridge_skill_name)
               ▼
    ┌──────────────────────┐
    │  Nova Bridge         │   separate repo, port 8001
    │  (holds credentials) │   enforces auth, caps, allowlist
    └──────────┬───────────┘
               │
               ▼
    Bybit V5 / Base Mainnet

## Tenant Isolation

- Every table carries `organization_id`
- Every ORM query filters by `organization_id`
- Cross-tenant reads return 404 (not 403) — avoids leaking existence
- JWT carries `org_id` and `role`, verified on every request

## Version Management

- `skills` and `skill_versions` are separate tables
- Versions are immutable — never updated in place
- Active version referenced by `skills.active_version_id`
- Only owners can activate (role checked from verified JWT, not client-supplied)

## Authorization

- JWT-based (OAuth2 password flow)
- bcrypt password hashing
- Role derived from the JWT claim — never from request body
- Owner-only activation and skill lifecycle changes

## Bridge Dispatch

Skills can optionally declare a `bridge_skill_name` in their
configuration. When present, execution is routed to Nova Bridge over
authenticated HTTP:

- Header: `X-Bridge-Token: <BRIDGE_SECRET>`
- Secret shared between Jarvis and the bridge, never sent to the LLM
- Jarvis refuses to start if `BRIDGE_SECRET` is unset
- Bridge failures surface as `status: "bridge_error"` — never silently masked

Jarvis holds no exchange API keys and no private keys. The bridge is the
only component with credentials.

## MCP Surface

`mcp_server.py` exposes Jarvis as an MCP server for LLM clients,
using the **MCP Python SDK v2** (`mcp.server.mcpserver.MCPServer`,
formerly `FastMCP`).

Tools exposed:
- `list_skills`
- `list_active_skills`
- `create_skill`
- `execute_skill`
- `run_agent`

Requires Python 3.10+ (SDK v2 constraint). Verified handshake:

    {"serverInfo":{"name":"jarvis-registry","version":"1.0.0"}}

## Audit Logging

Every action is logged with:

- `organization_id`
- `actor` (username)
- `event` (e.g. `executed_skill_23`, `created_version`)
- `version_id` where applicable
- timestamp

Two independent trails:
1. Jarvis DB (`audit_logs` table)
2. Nova Bridge log (`/tmp/nova_mcp_logs/skill_calls.log`) —
   includes rejected calls, not just successful ones

## Database Choice

- SQLite for local development — zero external dependencies
- PostgreSQL recommended for production (multi-writer concurrency,
  proper connection pooling, row-level security options)

## Testing

- `pytest -v` — 10/10 passing
- Covers: cross-tenant denial, non-owner activation denial,
  version immutability, audit-log correctness, idempotent activation
- Verified against a clean clone in a separate environment

## Known Limitations

- `/agent/run` uses mock tool-selection payloads; no live LLM call yet
- No pagination on list endpoints
- No Alembic migrations yet (schema auto-created via SQLAlchemy metadata)
- No rate limiting per org/token
- Not audited

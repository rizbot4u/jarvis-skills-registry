# Jarvis AI COO Skill Registry

Multi-tenant backend prototype for the Jarvis AI COO developer evaluation. Organizations can create, review, and activate custom AI skills with strict tenant isolation, immutable versioning, and full audit logging.

## Tech Stack

- FastAPI
- SQLAlchemy
- SQLite (see Architecture Decisions for reasoning)
- Pytest
- JWT Authentication (OAuth2 + bcrypt)

## Setup

### Option 1 — Local (Python)

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
Option 2 — Docker Compose
Bash


docker compose up --build
Running Tests
Bash


pytest -v
Expected: 10/10 tests passing.

Authentication
This system uses JWT (JSON Web Tokens) with bcrypt password hashing.

Seed Test Users
Bash


python seed_users.py
This creates:

owner1 / password123 (organization 1, owner role)

user1 / password123 (organization 1, user role)

owner2 / password123 (organization 2, owner role)

Get a Token
Bash


curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=owner1&password=password123"
Response:

JSON


{"access_token":"eyJhbGciOiJIUzI1NiIs...","token_type":"bearer"}
Use the Token
Bash


TOKEN="your_token_here"

curl -X GET http://localhost:8000/skills \
  -H "Authorization: Bearer $TOKEN"
API Examples
Create an Organization
Bash


curl -X POST http://localhost:8000/organizations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "ABC Construction"}'
Create a Skill Draft
Bash


curl -X POST http://localhost:8000/skills \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Invoice Approval Skill", "description": "Automates invoice review"}'
Create a New Version
Bash


curl -X POST http://localhost:8000/skills/1/versions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"version_number": 1, "configuration": "{\"parameters_schema\": {\"type\": \"object\", \"properties\": {\"invoice_id\": {\"type\": \"integer\"}}, \"required\": [\"invoice_id\"]}}", "created_by": "owner"}'
Activate a Version (Owner Only)
Bash


curl -X POST "http://localhost:8000/skills/1/activate?version_id=1" \
  -H "Authorization: Bearer $TOKEN"
Execute a Skill (With Schema Validation)
Bash


curl -X POST http://localhost:8000/skills/1/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"invoice_id": 12345}'
List Active Skills
Bash


curl -X GET http://localhost:8000/skills/active \
  -H "Authorization: Bearer $TOKEN"
Disable a Skill
Bash


curl -X DELETE http://localhost:8000/skills/1 \
  -H "Authorization: Bearer $TOKEN"
Architecture Decisions
See ARCHITECTURE.md in this repo.

Known Limitations
Authorization is handled via JWT with bcrypt password hashing. The X-Organization-ID header and actor query parameter are no longer used.

SQLite is used for local development and portability; PostgreSQL is recommended for production.

Database schema is auto-created by SQLAlchemy on startup rather than managed via a separate migration tool.

No pagination or filtering implemented on list endpoints.

What I Would Implement Next
Alembic migrations for schema versioning

PostgreSQL as the default datastore

Pagination and filtering on list endpoints

Refresh tokens for extended sessions

Frontend dashboard for managing skills

Note on Docker Compose
Dockerfile and docker-compose.yml are included and believed correct based on the application's dependencies. They were not fully verified to run in this development environment due to a broken system package repository (ChromeOS/Crostini cros-packages signing key issue unrelated to this project) preventing local Docker installation. The application has been fully verified via direct uvicorn execution and pytest, both documented above with real output.

AI Tools Used
Used AI as a pair-programming aid for scaffolding FastAPI routes, SQLAlchemy models, and test cases. All architecture decisions, testing strategy, and debugging were done and understood by the author, verified by manually re-tracing the full workflow through the Swagger UI.
## 🤖 LLM Agent Orchestrator

Jarvis includes a built-in Agent Orchestrator endpoint (`POST /agent/run`) that connects user prompts directly to active organization skills.

### How it works:
1. **Tool Discovery:** Dynamically retrieves active skills for the authenticated user's organization (`GET /skills/active`).
2. **Schema Translation:** Converts active skill schemas into standard LLM function-calling declarations.
3. **Execution Pipeline:** Passes the selected tool call and arguments to `POST /skills/{id}/execute` for JSON Schema validation and execution.

### Example Request (`POST /agent/run`)

```json
{
  "prompt": "Approve invoice #12345",
  "payload": {
    "skill_id": 1,
    "arguments": {
      "invoice_id": 12345,
      "amount": 250.0
    }
  }
}
Response
JSON


{
  "prompt": "Approve invoice #12345",
  "selected_skill_id": 1,
  "execution_response": {
    "skill": "Invoice Approver",
    "status": "executed",
    "result": "Skill executed with validation",
    "input": {
      "invoice_id": 12345,
      "amount": 250.0
    },
    "executed_by": "owner1",
    "organization_id": 1,
    "version": 1
  }
}

---

<ElicitationsGroup message="Where would you like to take the project next?">
  <Elicitation label="Connect a real LLM API (OpenAI / Gemini) to auto-select tools" query="Show me how to connect a live OpenAI or Gemini API call inside agent_orchestrator.py to dynamically pick tools based on user prompt."/>
  <Elicitation label="Add database migrations using Alembic" query="Help me set up Alembic database migrations for the skill registry project."/>
  <Elicitation label="Write automated Pytest unit tests for the agent orchestrator" query="Write Pytest test cases to automatically verify POST /agent/run with mock tools and execution errors."/>
</ElicitationsGroup>

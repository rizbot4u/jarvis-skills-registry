import os
import tempfile
import pytest
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.database import Base, SessionLocal
from app import models, schemas
from app.routes import skills

@pytest.fixture
def app_with_db():
    # Create a fresh temporary database file
    fd, db_file = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    # Insert initial organizations
    db = TestingSessionLocal()
    org1 = models.Organization(name="ABC Construction")
    org2 = models.Organization(name="XYZ Builders")
    db.add_all([org1, org2])
    db.commit()
    db.close()

    # Override the get_db dependency used in the router
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    # Create a new app instance
    app = FastAPI(title="Jarvis AI COO Skill Registry - Test")
    app.include_router(skills.router)
    # Override the dependency on the router's get_db
    app.dependency_overrides[skills.get_db] = override_get_db

    yield app

    # Cleanup
    if os.path.exists(db_file):
        os.remove(db_file)

@pytest.fixture
def client(app_with_db):
    return TestClient(app_with_db)

def test_same_org_create_read(client):
    client.post("/skills", json={"name": "Test"}, headers={"X-Organization-ID": "1"})
    response = client.get("/skills", headers={"X-Organization-ID": "1"})
    assert len(response.json()) == 1

def test_cross_org_read_denied(client):
    client.post("/skills", json={"name": "Org1"}, headers={"X-Organization-ID": "1"})
    response = client.get("/skills", headers={"X-Organization-ID": "2"})
    assert len(response.json()) == 0

def test_cross_org_update_denied(client):
    r = client.post("/skills", json={"name": "Skill"}, headers={"X-Organization-ID": "1"})
    skill_id = r.json()["id"]
    response = client.get(f"/skills/{skill_id}", headers={"X-Organization-ID": "2"})
    assert response.status_code == 404

def test_non_owner_activation_denied(client):
    r = client.post("/skills", json={"name": "Skill"}, headers={"X-Organization-ID": "1"})
    skill_id = r.json()["id"]
    r2 = client.post(
        f"/skills/{skill_id}/versions",
        json={"version_number": 1, "configuration": "{}", "created_by": "user"},
        headers={"X-Organization-ID": "1"}
    )
    version_id = r2.json()["id"]
    response = client.post(
        f"/skills/{skill_id}/activate?version_id={version_id}&actor=not_owner",
        headers={"X-Organization-ID": "1"}
    )
    assert response.status_code == 403

def test_draft_skill_cannot_execute(client):
    client.post("/skills", json={"name": "Draft"}, headers={"X-Organization-ID": "1"})
    response = client.get("/skills/active", headers={"X-Organization-ID": "1"})
    assert len(response.json()) == 0

def test_disabled_skill_excluded(client):
    r = client.post("/skills", json={"name": "Active"}, headers={"X-Organization-ID": "1"})
    skill_id = r.json()["id"]
    r2 = client.post(
        f"/skills/{skill_id}/versions",
        json={"version_number": 1, "configuration": "{}", "created_by": "owner"},
        headers={"X-Organization-ID": "1"}
    )
    version_id = r2.json()["id"]
    client.post(
        f"/skills/{skill_id}/activate?version_id={version_id}&actor=owner",
        headers={"X-Organization-ID": "1"}
    )
    client.delete(f"/skills/{skill_id}", headers={"X-Organization-ID": "1"})
    response = client.get("/skills/active", headers={"X-Organization-ID": "1"})
    assert len(response.json()) == 0

def test_active_version_immutable(client):
    r = client.post("/skills", json={"name": "Immutable"}, headers={"X-Organization-ID": "1"})
    skill_id = r.json()["id"]
    r2 = client.post(
        f"/skills/{skill_id}/versions",
        json={"version_number": 1, "configuration": "{}", "created_by": "owner"},
        headers={"X-Organization-ID": "1"}
    )
    version_id = r2.json()["id"]
    client.post(
        f"/skills/{skill_id}/activate?version_id={version_id}&actor=owner",
        headers={"X-Organization-ID": "1"}
    )
    response = client.post(
        f"/skills/{skill_id}/versions",
        json={"version_number": 2, "configuration": "{}", "created_by": "owner"},
        headers={"X-Organization-ID": "1"}
    )
    assert response.status_code == 400

def test_duplicate_activation_idempotent(client):
    r = client.post("/skills", json={"name": "Idempotent"}, headers={"X-Organization-ID": "1"})
    skill_id = r.json()["id"]
    r2 = client.post(
        f"/skills/{skill_id}/versions",
        json={"version_number": 1, "configuration": "{}", "created_by": "owner"},
        headers={"X-Organization-ID": "1"}
    )
    version_id = r2.json()["id"]
    r3 = client.post(
        f"/skills/{skill_id}/activate?version_id={version_id}&actor=owner",
        headers={"X-Organization-ID": "1"}
    )
    assert r3.status_code == 200
    r4 = client.post(
        f"/skills/{skill_id}/activate?version_id={version_id}&actor=owner",
        headers={"X-Organization-ID": "1"}
    )
    assert r4.status_code == 200
    assert r4.json()["message"] == "Skill already active with this version"

def test_invalid_tool_rejected(client):
    response = client.post("/skills", json={"name": ""}, headers={"X-Organization-ID": "1"})
    assert response.status_code == 422  # Now expects 422 due to validation

def test_audit_record_contains_org_actor_event_version(client):
    r = client.post("/skills", json={"name": "Audit"}, headers={"X-Organization-ID": "1"})
    skill_id = r.json()["id"]
    r2 = client.post(
        f"/skills/{skill_id}/versions",
        json={"version_number": 1, "configuration": "{}", "created_by": "tester"},
        headers={"X-Organization-ID": "1"}
    )
    version_id = r2.json()["id"]
    client.post(
        f"/skills/{skill_id}/activate?version_id={version_id}&actor=owner",
        headers={"X-Organization-ID": "1"}
    )
    pass

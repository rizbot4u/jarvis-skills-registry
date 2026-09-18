#!/usr/bin/env python3
import requests

BASE = "http://localhost:8000"

def get_token(username, password):
    r = requests.post(f"{BASE}/token",
                      headers={"Content-Type": "application/x-www-form-urlencoded"},
                      data={"username": username, "password": password})
    r.raise_for_status()
    return r.json()["access_token"]

def create_skill(token, name):
    r = requests.post(f"{BASE}/skills",
                      headers={"Authorization": f"Bearer {token}",
                               "Content-Type": "application/json"},
                      json={"name": name, "description": "Tenant isolation test"})
    r.raise_for_status()
    return r.json()["id"]

def create_version(token, skill_id):
    payload = {
        "version_number": 1,
        "configuration": "{\"parameters_schema\":{\"type\":\"object\",\"properties\":{\"invoice_id\":{\"type\":\"integer\"}},\"required\":[\"invoice_id\"]}}",
        "created_by": "owner1"
    }
    r = requests.post(f"{BASE}/skills/{skill_id}/versions",
                      headers={"Authorization": f"Bearer {token}",
                               "Content-Type": "application/json"},
                      json=payload)
    r.raise_for_status()
    return r.json()["id"]

def activate_version(token, skill_id, version_id):
    r = requests.post(f"{BASE}/skills/{skill_id}/activate?version_id={version_id}",
                      headers={"Authorization": f"Bearer {token}"})
    return r.status_code, r.json()

def execute_skill(token, skill_id):
    r = requests.post(f"{BASE}/skills/{skill_id}/execute",
                      headers={"Authorization": f"Bearer {token}",
                               "Content-Type": "application/json"},
                      json={"invoice_id": 12345})
    return r.status_code, r.json()

def update_skill(token, skill_id):
    r = requests.put(f"{BASE}/skills/{skill_id}",
                     headers={"Authorization": f"Bearer {token}",
                              "Content-Type": "application/json"},
                     json={"name": "Updated Name"})
    return r.status_code, r.json()

def read_skill(token, skill_id):
    r = requests.get(f"{BASE}/skills/{skill_id}",
                     headers={"Authorization": f"Bearer {token}"})
    return r.status_code, r.json()

if __name__ == "__main__":
    # Tokens for two different org users
    token_owner1 = get_token("owner1", "yourpass")
    token_owner2 = get_token("owner2", "otherpass")

    # Owner1 creates skill + version + activates
    skill_id = create_skill(token_owner1, "Invoice Approver")
    version_id = create_version(token_owner1, skill_id)
    print("Owner1 activate:", activate_version(token_owner1, skill_id, version_id))
    print("Owner1 execute:", execute_skill(token_owner1, skill_id))

    # Owner2 attempts cross‑org operations
    print("Owner2 read attempt:", read_skill(token_owner2, skill_id))
    print("Owner2 update attempt:", update_skill(token_owner2, skill_id))
    print("Owner2 execute attempt:", execute_skill(token_owner2, skill_id))
    print("Owner2 activate attempt:", activate_version(token_owner2, skill_id, version_id))

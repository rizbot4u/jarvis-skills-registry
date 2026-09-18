#!/usr/bin/env python3
import requests

BASE_REGISTRY = "http://localhost:8000"
BASE_BYBIT = "http://localhost:3000"

USERNAME = "owner1"
PASSWORD = "yourpass"

def get_token():
    r = requests.post(f"{BASE_REGISTRY}/token",
                      headers={"Content-Type": "application/x-www-form-urlencoded"},
                      data={"username": USERNAME, "password": PASSWORD})
    r.raise_for_status()
    return r.json()["access_token"]

def create_skill(token):
    r = requests.post(f"{BASE_REGISTRY}/skills",
                      headers={"Authorization": f"Bearer {token}",
                               "Content-Type": "application/json"},
                      json={"name": "Invoice Approver", "description": "Approves invoices"})
    r.raise_for_status()
    return r.json()["id"]

def create_version(token, skill_id):
    payload = {
        "version_number": 1,
        "configuration": "{\"parameters_schema\":{\"type\":\"object\",\"properties\":{\"invoice_id\":{\"type\":\"integer\"}},\"required\":[\"invoice_id\"]}}",
        "created_by": USERNAME
    }
    r = requests.post(f"{BASE_REGISTRY}/skills/{skill_id}/versions",
                      headers={"Authorization": f"Bearer {token}",
                               "Content-Type": "application/json"},
                      json=payload)
    r.raise_for_status()
    return r.json()["id"]

def activate_version(token, skill_id, version_id):
    r = requests.post(f"{BASE_REGISTRY}/skills/{skill_id}/activate?version_id={version_id}",
                      headers={"Authorization": f"Bearer {token}"})
    r.raise_for_status()
    return r.json()

def execute_skill(token, skill_id):
    r = requests.post(f"{BASE_REGISTRY}/skills/{skill_id}/execute",
                      headers={"Authorization": f"Bearer {token}",
                               "Content-Type": "application/json"},
                      json={"invoice_id": 12345})
    r.raise_for_status()
    return r.json()

def agent_run(token, skill_id):
    payload = {
        "prompt": "Approve invoice #12345",
        "payload": {"skill_id": skill_id, "arguments": {"invoice_id": 12345}}
    }
    r = requests.post(f"{BASE_REGISTRY}/agent/run",
                      headers={"Authorization": f"Bearer {token}",
                               "Content-Type": "application/json"},
                      json=payload)
    r.raise_for_status()
    return r.json()

def place_order():
    payload = {"symbol": "BTCUSDT", "side": "Buy", "qty": 0.01}
    r = requests.post(f"{BASE_BYBIT}/place_order",
                      headers={"Content-Type": "application/json"},
                      json=payload)
    return r.json()

if __name__ == "__main__":
    token = get_token()
    skill_id = create_skill(token)
    version_id = create_version(token, skill_id)
    print("Activated:", activate_version(token, skill_id, version_id))
    print("Executed:", execute_skill(token, skill_id))
    print("Agent run:", agent_run(token, skill_id))
    try:
        print("Bybit order:", place_order())
    except Exception as e:
        print("Bybit MCP not running or unauthenticated:", e)

#!/usr/bin/env python3
"""
Register all six Nova Bridge skills in Jarvis's registry.
Idempotent: skips any skill whose name already exists.
"""
import json
import requests

JARVIS = "http://localhost:8000"

SKILLS = [
    {
        "name": "Bybit Ticker",
        "description": "Live CEX market data via Nova Bridge",
        "bridge_skill_name": "bybit.ticker",
        "parameters_schema": {
            "type": "object",
            "properties": {
                "symbol":   {"type": "string", "description": "e.g. BTCUSDT"},
                "category": {"type": "string", "description": "spot | linear | inverse"},
            },
            "required": ["symbol"],
        },
    },
    {
        "name": "Bybit Balance",
        "description": "Read Bybit account balance",
        "bridge_skill_name": "bybit.balance",
        "parameters_schema": {
            "type": "object",
            "properties": {
                "accountType": {"type": "string", "description": "UNIFIED | SPOT | CONTRACT"},
            },
        },
    },
    {
        "name": "Bybit Order",
        "description": "Place a Bybit order (requires confirm: true)",
        "bridge_skill_name": "bybit.order",
        "parameters_schema": {
            "type": "object",
            "properties": {
                "symbol":    {"type": "string"},
                "side":      {"type": "string", "enum": ["Buy", "Sell"]},
                "orderType": {"type": "string", "enum": ["Market", "Limit"]},
                "qty":       {"type": "string"},
                "price":     {"type": "string"},
                "category":  {"type": "string"},
                "confirm":   {"type": "boolean"},
            },
            "required": ["symbol", "side", "qty", "confirm"],
        },
    },
    {
        "name": "DKHYR Info",
        "description": "DKHYR token metadata (Base Mainnet)",
        "bridge_skill_name": "dkhyr.info",
        "parameters_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "DKHYR Balance",
        "description": "Read DKHYR balance for an address",
        "bridge_skill_name": "dkhyr.balance",
        "parameters_schema": {
            "type": "object",
            "properties": {"address": {"type": "string"}},
            "required": ["address"],
        },
    },
    {
        "name": "DKHYR Transfer",
        "description": "Send DKHYR on Base (requires TREASURY_PRIVATE_KEY)",
        "bridge_skill_name": "dkhyr.transfer",
        "parameters_schema": {
            "type": "object",
            "properties": {
                "to_address": {"type": "string"},
                "amount":     {"type": "string"},
            },
            "required": ["to_address", "amount"],
        },
    },
]


def main():
    # 1. auth
    tok = requests.post(
        f"{JARVIS}/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"username": "owner1", "password": "password123"},
    ).json()["access_token"]
    H = {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}
    print("✅ auth")

    # 2. list existing to avoid dupes
    existing = {s["name"] for s in requests.get(f"{JARVIS}/skills", headers=H).json()}
    print(f"   existing skills: {len(existing)}")

    # 3. create + version + activate each
    for spec in SKILLS:
        name = spec["name"]
        if name in existing:
            print(f"⏭  {name} already exists — skipping")
            continue

        # create
        s = requests.post(f"{JARVIS}/skills", headers=H,
            json={"name": name, "description": spec["description"]}).json()
        sid = s["id"]

        # version with bridge config
        cfg = {
            "parameters_schema": spec["parameters_schema"],
            "bridge_skill_name": spec["bridge_skill_name"],
        }
        v = requests.post(f"{JARVIS}/skills/{sid}/versions", headers=H,
            json={
                "version_number": 1,
                "created_by": "owner1",
                "configuration": json.dumps(cfg),
            }).json()
        vid = v["id"]

        # activate
        requests.post(f"{JARVIS}/skills/{sid}/activate?version_id={vid}", headers=H)

        print(f"✅ {name}  →  skill_id={sid}  version_id={vid}  bridge={spec['bridge_skill_name']}")

    print("\nAll skills registered. Test with:")
    print("  python3 -c \"import requests,json; "
          "t=requests.post('http://localhost:8000/token',"
          "headers={'Content-Type':'application/x-www-form-urlencoded'},"
          "data={'username':'owner1','password':'password123'}).json()['access_token']; "
          "H={'Authorization':f'Bearer {t}','Content-Type':'application/json'}; "
          "print(json.dumps(requests.post('http://localhost:8000/skills/21/execute',"
          "headers=H,json={'symbol':'BTCUSDT','category':'linear'}).json(),indent=2))\"")


if __name__ == "__main__":
    main()

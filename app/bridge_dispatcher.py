"""
Routes Jarvis skill execution to the Nova MCP Bridge when a skill's
configuration contains the key 'bridge_skill_name'.

The bridge requires an X-Bridge-Token header matching BRIDGE_SECRET.
Jarvis refuses to start if BRIDGE_SECRET is not set.
"""
import json
import os
import requests

BRIDGE_URL = os.getenv("BRIDGE_URL", "http://localhost:8001/skills/execute")
BRIDGE_TIMEOUT_SEC = 15
BRIDGE_SECRET = os.getenv("BRIDGE_SECRET")

if not BRIDGE_SECRET:
    raise RuntimeError(
        "BRIDGE_SECRET is not set. Add it to Jarvis's .env "
        "(must match the value used by ~/nova_mcp/.env)."
    )


def execute_bridge_skill(skill_name: str, parameters: dict) -> dict:
    try:
        r = requests.post(
            BRIDGE_URL,
            headers={
                "Content-Type": "application/json",
                "X-Bridge-Token": BRIDGE_SECRET,
            },
            json={
                "skill_name": skill_name,
                "org_id": "org_1",
                "actor": "jarvis",
                "parameters": parameters,
            },
            timeout=BRIDGE_TIMEOUT_SEC,
        )
        if r.status_code == 401:
            return {
                "status": "bridge_error",
                "skill_name": skill_name,
                "message": "401 unauthorized — BRIDGE_SECRET mismatch between Jarvis and Nova Bridge",
            }
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        return {
            "status": "bridge_error",
            "skill_name": skill_name,
            "message": f"Bridge call failed: {e}",
        }


def execute_skill_with_bridge_routing(skill, active_version, parameters, actor, org_id):
    raw = active_version.configuration
    config = json.loads(raw) if isinstance(raw, str) else (raw or {})

    bridge_name = config.get("bridge_skill_name")
    if bridge_name:
        result = execute_bridge_skill(bridge_name, parameters)
        status = "bridge_error" if result.get("status") == "bridge_error" else "executed_via_bridge"
        return {
            "skill": skill.name,
            "status": status,
            "result": result,
            "input": parameters,
            "executed_by": actor,
            "organization_id": org_id,
            "version": active_version.version_number,
        }

    return {
        "skill": skill.name,
        "status": "executed",
        "result": "Skill executed with validation",
        "input": parameters,
        "executed_by": actor,
        "organization_id": org_id,
        "version": active_version.version_number,
    }

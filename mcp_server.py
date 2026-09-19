#!/usr/bin/env python3
"""
Jarvis Skill Registry — MCP Server (SDK v2)
Wraps FastAPI endpoints as MCP tools.
"""

import os
import httpx
from mcp.server.mcpserver import MCPServer
from dotenv import load_dotenv

load_dotenv()

# Config
BASE_URL = os.getenv("JARVIS_URL", "http://127.0.0.1:8000")
DEFAULT_USER = os.getenv("JARVIS_USER", "owner1")
DEFAULT_PASS = os.getenv("JARVIS_PASS", "password123")

mcp = MCPServer("jarvis-registry", version="1.0.0")

# Cache token
_token_cache = {"token": None}


async def get_token() -> str:
    """Login and cache a JWT."""
    if _token_cache["token"]:
        return _token_cache["token"]
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BASE_URL}/token",
            data={"username": DEFAULT_USER, "password": DEFAULT_PASS},
        )
        r.raise_for_status()
        _token_cache["token"] = r.json()["access_token"]
        return _token_cache["token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@mcp.tool()
async def list_skills() -> list:
    """List all skills for the authenticated organization."""
    token = await get_token()
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/skills", headers=auth_headers(token))
        return r.json()


@mcp.tool()
async def list_active_skills() -> list:
    """List only active skills for the authenticated organization."""
    token = await get_token()
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/skills/active", headers=auth_headers(token))
        return r.json()


@mcp.tool()
async def create_skill(name: str, description: str = "") -> dict:
    """Create a new draft skill."""
    token = await get_token()
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BASE_URL}/skills",
            headers=auth_headers(token),
            json={"name": name, "description": description},
        )
        return r.json()


@mcp.tool()
async def execute_skill(skill_id: int, arguments: dict) -> dict:
    """Execute a skill with the given arguments."""
    token = await get_token()
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BASE_URL}/skills/{skill_id}/execute",
            headers=auth_headers(token),
            json=arguments,
        )
        return r.json()


@mcp.tool()
async def run_agent(prompt: str, skill_id: int, arguments: dict) -> dict:
    """Run the LLM Agent Orchestrator against the skill registry."""
    token = await get_token()
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BASE_URL}/agent/run",
            headers=auth_headers(token),
            json={
                "prompt": prompt,
                "payload": {"skill_id": skill_id, "arguments": arguments},
            },
        )
        return r.json()


if __name__ == "__main__":
    mcp.run()

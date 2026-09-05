import json
import httpx
from typing import Any, Dict, List

BASE_URL = "http://127.0.0.1:8000"

class JarvisAgentOrchestrator:
    def __init__(self, auth_token: str):
        self.auth_token = auth_token
        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }

    def fetch_active_skills(self) -> List[Dict[str, Any]]:
        """Pull all active skills for the caller's organization."""
        with httpx.Client() as client:
            response = client.get(f"{BASE_URL}/skills/active", headers=self.headers)
            response.raise_for_status()
            return response.json()

    def format_skills_for_llm(self, skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map registry skills to standard LLM function-calling declarations."""
        tools = []
        for skill in skills:
            raw_config = skill.get("active_version", {}).get("configuration", "{}")
            try:
                config = json.loads(raw_config) if isinstance(raw_config, str) else raw_config
                parameters = config.get("parameters_schema", config)
            except json.JSONDecodeError:
                parameters = {"type": "object", "properties": {}}
            
            tools.append({
                "type": "function",
                "function": {
                    "name": f"skill_{skill['id']}",
                    "description": skill.get("description") or f"Execute {skill['name']}",
                    "parameters": parameters
                }
            })
        return tools

    def execute_skill_call(self, skill_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch the LLM's selected tool call to the execution pipeline."""
        with httpx.Client() as client:
            response = client.post(
                f"{BASE_URL}/skills/{skill_id}/execute",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()

    def run_agent_loop(self, user_prompt: str, mock_llm_choice: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        1. Fetch active skills from registry
        2. Format tools for LLM
        3. Parse LLM choice and trigger execution pipeline
        """
        active_skills = self.fetch_active_skills()
        tools = self.format_skills_for_llm(active_skills)
        
        if not tools:
            return {"status": "error", "message": "No active skills available for this organization."}
        
        # Select target skill (default to first active skill)
        target_skill = active_skills[0]
        
        # Use passed mock choice or build a payload matching the schema
        if mock_llm_choice:
            selected_tool = mock_llm_choice
        else:
            selected_tool = {
                "skill_id": target_skill["id"],
                "arguments": {"invoice_id": 12345}  # Valid payload matching schema
            }
        
        # Trigger execution via API pipeline
        execution_result = self.execute_skill_call(
            skill_id=selected_tool["skill_id"],
            payload=selected_tool["arguments"]
        )
        
        return {
            "prompt": user_prompt,
            "selected_skill_id": selected_tool["skill_id"],
            "execution_response": execution_result
        }

import subprocess
import json
from app.services.agent_orchestrator import JarvisAgentOrchestrator

# 1. Obtain JWT Token
token_cmd = """curl -s -X POST http://localhost:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=owner1&password=password123" """
res = subprocess.check_output(token_cmd, shell=True)
token = json.loads(res)["access_token"]

# 2. Initialize orchestrator
orchestrator = JarvisAgentOrchestrator(auth_token=token)

# 3. Load active skills
skills = orchestrator.fetch_active_skills()
print(f"✅ Loaded {len(skills)} active skills into LLM context.")

if not skills:
    print("❌ No active skills found. Ensure step 2 completed successfully.")
    exit(1)

# Pick the latest active skill ("Invoice Approver")
target_skill = skills[-1]
print(f"\n🚀 Testing execution on Skill #{target_skill['id']} ({target_skill['name']})...")

result = orchestrator.run_agent_loop(
    user_prompt="Approve invoice #12345",
    mock_llm_choice={
        "skill_id": target_skill["id"],
        "arguments": {"invoice_id": 12345, "amount": 250.00}
    }
)

print("\n🎉 Execution Result:")
print(json.dumps(result, indent=2))

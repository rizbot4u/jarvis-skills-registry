#!/bin/bash
# ============================================================
# Jarvis Skill Registry — Final Cleanup & Verification
# ============================================================

set -e
cd ~/jarvis-skills-registry-fresh
source venv/bin/activate

echo "=========================================="
echo " STEP 1: Fix duplicate operation ID"
echo "=========================================="
# Rename execute_skill -> run_skill_execution in execution.py
if grep -q "def execute_skill" app/routers/execution.py; then
    sed -i 's/def execute_skill(/def run_skill_execution(/' app/routers/execution.py
    echo "✅ Renamed execute_skill -> run_skill_execution"
else
    echo "ℹ️  Already renamed or not found"
fi

echo ""
echo "=========================================="
echo " STEP 2: Fix SQLAlchemy 2.0 import"
echo "=========================================="
if grep -q "from sqlalchemy.ext.declarative import declarative_base" app/database.py; then
    sed -i 's|from sqlalchemy.ext.declarative import declarative_base|from sqlalchemy.orm import declarative_base|' app/database.py
    echo "✅ Modernized declarative_base import"
else
    echo "ℹ️  Already modern or not found"
fi

echo ""
echo "=========================================="
echo " STEP 3: Clean requirements.txt"
echo "=========================================="
grep -q "python-multipart" requirements.txt || echo "python-multipart" >> requirements.txt
grep -q "bcrypt==4.0.1" requirements.txt || echo "bcrypt==4.0.1" >> requirements.txt
echo "✅ requirements.txt updated"
cat requirements.txt

echo ""
echo "=========================================="
echo " STEP 4: Preserve Bybit trading code as separate file"
echo "=========================================="
cat > bybit_trading.py << 'BYBIT_EOF'
"""
Bybit V5 API — Standalone Trading Client
Kept separate from the FastAPI app (main.py).
"""
import hmac
import hashlib
import time
import json
import requests

BYBIT_API_URL = "https://api.bybit.com"


def execute_bybit_order(symbol, side, order_type, qty, price=None,
                        api_key="", api_secret=""):
    """Place a signed order on Bybit V5."""
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"

    payload = {
        "category": "linear",
        "symbol": symbol,
        "side": side,
        "orderType": order_type,
        "qty": qty,
        "timeInForce": "GTC",
    }
    if price:
        payload["price"] = price

    body = json.dumps(payload, separators=(",", ":"))
    param_str = timestamp + api_key + recv_window + body

    signature = hmac.new(
        api_secret.encode("utf-8"),
        param_str.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-SIGN": signature,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
        "Content-Type": "application/json",
    }

    r = requests.post(f"{BYBIT_API_URL}/v5/order/create",
                      headers=headers, data=body, timeout=15)
    return r.json()


if __name__ == "__main__":
    print("Bybit trading client loaded. Import execute_bybit_order to use.")
BYBIT_EOF
echo "✅ bybit_trading.py created"

echo ""
echo "=========================================="
echo " STEP 5: Run tests"
echo "=========================================="
pytest -v 2>&1 | tail -15

echo ""
echo "=========================================="
echo " STEP 6: Start server in background for smoke test"
echo "=========================================="
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 &
SERVER_PID=$!
sleep 4

echo ""
echo "=========================================="
echo " STEP 7: Smoke test endpoints"
echo "=========================================="
BASE=http://127.0.0.1:8000

curl -s $BASE/ ; echo ""
echo ""

# Login
TOKEN=$(curl -s -X POST $BASE/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=owner1&password=password123" \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "Token: ${TOKEN:0:40}..."
echo ""

# List skills
echo "Skills:"
curl -s $BASE/skills -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# List active
echo "Active:"
curl -s $BASE/skills/active -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo ""
echo "=========================================="
echo " STEP 8: Stop server"
echo "=========================================="
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null || true
echo "✅ Server stopped"

echo ""
echo "=========================================="
echo " STEP 9: Commit changes"
echo "=========================================="
git add -A
git status
git commit -m "Fix warnings, add bybit_trading.py, clean requirements" || echo "No changes to commit"

echo ""
echo "=========================================="
echo " ✅ FINALIZATION COMPLETE"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. git push origin main"
echo "  2. Screenshot the pytest output above"
echo "  3. Start server: python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""

#!/usr/bin/env python3
"""Nova end-to-end demo: natural language → Jarvis → Bridge → Bybit."""
import requests, json, sys

BASE = "http://localhost:8000"
BRIDGE = "http://localhost:8001"

def line(t): print(f"\n{'━'*60}\n{t}\n{'━'*60}")

line("0 · Both services reachable")
print("Bridge:", requests.get(BRIDGE+"/", timeout=3).json()["service"])
print("Jarvis:", requests.get(BASE+"/", timeout=3).json()["message"])

line("1 · Authenticate (owner1)")
tok = requests.post(f"{BASE}/token",
    headers={"Content-Type":"application/x-www-form-urlencoded"},
    data={"username":"owner1","password":"password123"}).json()["access_token"]
H = {"Authorization": f"Bearer {tok}", "Content-Type":"application/json"}
print("✅ token acquired")

line("2 · Register a natural-language skill: 'Bybit Ticker Bridge'")
s = requests.post(f"{BASE}/skills", headers=H,
    json={"name":"Bybit Ticker Bridge",
          "description":"Say 'what's BTC doing?' → live Bybit price"}).json()
sid = s["id"]
print(f"skill_id = {sid}")

line("3 · Attach bridge routing: bridge_skill_name = bybit.ticker")
v = requests.post(f"{BASE}/skills/{sid}/versions", headers=H,
    json={"version_number":1,"created_by":"owner1","configuration":json.dumps({
        "parameters_schema":{"type":"object",
            "properties":{"symbol":{"type":"string"},"category":{"type":"string"}},
            "required":["symbol"]},
        "bridge_skill_name":"bybit.ticker"})}).json()
requests.post(f"{BASE}/skills/{sid}/activate?version_id={v['id']}", headers=H)
print("✅ activated")

line("4 · Execute via Jarvis → Bridge → Bybit")
r = requests.post(f"{BASE}/skills/{sid}/execute", headers=H,
    json={"symbol":"BTCUSDT","category":"linear"}).json()

assert r["status"] == "executed_via_bridge", r
t = r["result"]["result"]["result"]["list"][0]

line("5 · Result")
print(f"  Symbol        : {t['symbol']}")
print(f"  Last price    : ${t['lastPrice']}")
print(f"  24h change    : {float(t['price24hPcnt'])*100:+.2f}%")
print(f"  24h high/low  : ${t['highPrice24h']} / ${t['lowPrice24h']}")
print(f"  24h volume    : {t['volume24h']} BTC")
print(f"\n  Routed through: Jarvis (py) → Nova Bridge (node) → Bybit V5")
print(f"  Executed by   : {r['executed_by']}  org={r['organization_id']}")
print(f"\n🎉 PIPELINE LIVE")

#!/usr/bin/env python3
"""
Bridge: Telegram → Jarvis Registry → Bybit MCP → Audit Log
"""
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import httpx

app = FastAPI(title="Nova Bridge")

BYBIT_MCP_URL = "http://localhost:3000"  # Bybit MCP HTTP endpoint
JARVIS_URL = "http://localhost:8000"


class TradeRequest(BaseModel):
    symbol: str
    side: str          # "Buy" or "Sell"
    qty: float
    uid: str           # your broker UID


@app.post("/trade/execute")
async def execute_trade(req: TradeRequest):
    async with httpx.AsyncClient(timeout=30) as client:
        # 1. Ask Bybit MCP to place the order
        mcp_response = await client.post(
            f"{BYBIT_MCP_URL}/tools/place_order",
            json={
                "category": "spot",
                "symbol": req.symbol,
                "side": req.side,
                "orderType": "Market",
                "qty": str(req.qty),
            }
        )
        mcp_result = mcp_response.json()

        # 2. Log the execution in Jarvis Registry
        # (Requires a skill created for "Place Trade")
        jarvis_response = await client.post(
            f"{JARVIS_URL}/agent/run",
            headers={"Authorization": f"Bearer {req.uid}"},
            json={
                "prompt": f"{req.side} {req.qty} {req.symbol}",
                "payload": {
                    "skill_id": 2,
                    "arguments": {
                        "symbol": req.symbol,
                        "side": req.side,
                        "qty": req.qty,
                    }
                }
            }
        )

        return {
            "bybit_mcp": mcp_result,
            "jarvis_audit": jarvis_response.json(),
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)

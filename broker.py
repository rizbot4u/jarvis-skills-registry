import hmac
import hashlib
import time
import requests
import json
import os

# --- Configuration ---
# Load from environment or use fallback
API_KEY = os.getenv("BYBIT_API_KEY", "0KiOwBOlok3VjKeodk")
API_SECRET = os.getenv("BYBIT_API_SECRET", "o7lrTzgWsWYmX5ISbzybpRDLSp2BDWDExww8")
BROKER_ID = os.getenv("BROKER_CODE", "Kr000820")

# Base URL (Use https://api-testnet.bybit.com for Testnet)
BASE_URL = "https://api.bybit.com" 

def generate_signature(timestamp: str, recv_window: str, payload_str: str) -> str:
    """Generates Bybit V5 HMAC SHA256 Signature."""
    param_str = timestamp + API_KEY + recv_window + payload_str
    return hmac.new(
        API_SECRET.encode('utf-8'),
        param_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

def test_broker_order():
    url = f"{BASE_URL}/v5/order/create"
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"

    # Test Order Payload (Linear Perpetual)
    payload = {
        "category": "linear",
        "symbol": "BTCUSDT",
        "side": "Buy",
        "orderType": "Limit",
        "qty": "0.001",
        "price": "30000",  # Low limit price to avoid immediate execution
        "timeInForce": "GTC"
    }
    
    json_payload = json.dumps(payload)
    signature = generate_signature(timestamp, recv_window, json_payload)

    # HTTP Headers containing your Broker ID
    headers = {
        "X-BAPI-API-KEY": API_KEY,
        "X-BAPI-SIGN": signature,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
        "Content-Type": "application/json",
        "referer": BROKER_ID  # <-- CRITICAL: Credits $79M volume to Broker Kr000820
    }

    print(f"[+] Sending Order to Bybit V5 with Broker ID Header: {BROKER_ID}...")
    try:
        response = requests.post(url, headers=headers, data=json_payload)
        res_data = response.json()
        
        print("\n=== Bybit API Response ===")
        print(json.dumps(res_data, indent=2))
        
        if res_data.get("retCode") == 0:
            print("\n✅ Order successfully created and accredited to Broker ID Kr000820!")
        else:
            print(f"\n⚠️ API Returned Code {res_data.get('retCode')}: {res_data.get('retMsg')}")
            
    except Exception as e:
        print(f"\n❌ Request failed: {e}")

if __name__ == "__main__":
    test_broker_order()

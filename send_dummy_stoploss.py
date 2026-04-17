import sys
import os

# Ensure we can import from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "app")))

from app.utils.telegram import send_telegram

def send_dummy_stoploss():
    message = """
⚠️ *STOP LOSS ALERT (RECURRING)*

Node: `NYASHA`
Status: **VIOLATION DETECTED**

📉 Stock: **HDFCBANK.NS**
💰 Entry: ₹1,640.00
📊 Current: ₹1,550.00
📉 Loss: `-5.49%`

👉 **ACTION: SELL IMMEDIATELY**

---
*Alert will repeat every 1 hour until the asset is cleared from your node.*
"""
    send_telegram(message)
    print("Dummy Stop-Loss alert transmitted to Telegram.")

if __name__ == "__main__":
    send_dummy_stoploss()

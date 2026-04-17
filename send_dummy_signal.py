import sys
import os

# Ensure we can import from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "app")))

from app.utils.telegram import send_telegram

def send_dummy_rebalance():
    message = """
📊 *AI PORTFOLIO REBALANCE SIGNAL*

Node: `NYASHA_2030`
Status: **CRITICAL OPTIMIZATION REQUIRED**

---

🟢 **BUY: RELIANCE.NS**
↳ Score: `94/100` (Strong Bullish Vector)
↳ Target: ₹3,150.00

🟡 **HOLD: TCS.NS**
↳ Score: `78/100` (Consolidating Matrix)
↳ RSI: `54.2`

🔴 **SELL: ZOMATO.NS**
↳ Score: `32/100` (Momentum Failure)
↳ Action: Exit at Market Price

---

⚠️ *Uplink encrypted via Telegram Secure Node*
"""
    send_telegram(message)
    print("Dummy signal transmitted to Telegram.")

if __name__ == "__main__":
    send_dummy_rebalance()

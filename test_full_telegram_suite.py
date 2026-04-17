import requests
import time

BOT_TOKEN = "8645653053:AAEu9UKXSXL2mEly6sBfy6RFebL6YA5ftZA"
CHAT_ID = "5673785873"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        resp = requests.post(url, json=payload)
        return resp.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def run_suite():
    print("Initializing Multi-Module Telegram Test Suite...")

    # 1. AI Recommendation
    msg_1 = """🧠 <b>AI NEURAL SCAN: RECOMMENDATION</b>

Asset: <b>INFY (Infosys Ltd)</b>
Current Price: <b>₹1,540.20</b>
---------------------------
🎯 AI Confidence Score: <b>94.2%</b>
📡 Signal: <b>STRONG BUY</b>

📊 <b>Technical Intel:</b>
• Volume Breakout (+15% vs Avg)
• 3-Day Micro Surge Detected
• MACD Bullish Crossover (Daily)

📝 <b>Execution Guidance:</b>
Accumulate at current levels. Target: ₹1,680.
"""
    print("Sending AI Recommendation...")
    send_telegram(msg_1)
    time.sleep(2)

    # 2. Stoploss Alert (5% Drop)
    msg_2 = """🚨 <b>RISK ALERT: STOP-LOSS TRIGGER</b>

Asset: <b>RELIANCE.NS</b>
---------------------------
📉 <b>5.0% DRAWDOWN DETECTED</b>
Buy Price: ₹2,500.00
Current Price: ₹2,375.00

🛡️ <b>Initial Risk Phase:</b>
Your 5% safety buffer has been breached. 

❌ <b>Condition Met: Liquidation Advised.</b>
"""
    print("Sending Stop-Loss Alert...")
    send_telegram(msg_2)
    time.sleep(2)

    # 3. News Pulse
    msg_3 = """🌐 <b>NEURAL PULSE: MARKET NEWS</b>

Source: <b>Macro Oracle</b>
Impact: <code style="color: #ff4444">CRITICAL</code>
---------------------------
📰 <b>RBI Monetary Policy Committee Update</b>
The MPC has signaled a 'Wait and See' approach on interest rates. Markets reacting to high CPI data projections for the next quarter.

⚠️ <b>Volatility Warning:</b>
Expect high fluctuation in Banking sector nodes.
"""
    print("Sending News Update...")
    send_telegram(msg_3)
    time.sleep(2)

    # 4. Portfolio Summary
    msg_4 = """📊 <b>PORTFOLIO STATUS SUMMARY</b>
Node: <b>NARUTO_TRADER</b>

💰 Total Portfolio Value: <b>₹1,25,840.00</b>
📈 Net Performance: <b>+₹4,250.00 (3.5%)</b>
---------------------------
📦 <b>Current Holdings:</b>
• <b>RELIANCE</b> (10 Units) | +2.1%
• <b>INFY</b> (5 Units) | -1.5%
• <b>TATASTEEL</b> (20 Units) | +8.4%

🛡️ <b>Risk Status: SECURED</b>
3/3 Assets within Protected Zones.
"""
    print("Sending Portfolio Summary...")
    send_telegram(msg_4)

    print("\n✅ Suite Complete. Please check your Telegram.")

if __name__ == "__main__":
    run_suite()

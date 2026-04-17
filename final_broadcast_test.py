import requests
import time

BOT_TOKEN = "8645653053:AAEu9UKXSXL2mEly6sBfy6RFebL6YA5ftZA"
CHAT_ID = "5673785873"

def send_test_one_by_one():
    # TEMPLATES UPDATED TO HTML TO AVOID MARKDOWN PARSING BUGS (e.g. underscores in Names)
    alerts = [
        {
            "name": "INITIAL RISK",
            "msg": """🚨 <b>INITIAL RISK BUFFER HIT</b>\n\nNode: TEST_NODE\nAsset: <b>RELIANCE</b>\n---------------------------\n💰 Buy Price: ₹2,500.00\n🚀 Peak Price: ₹2,580.00\n🛑 Exit Floor: ₹2,375.00\n📊 Current: ₹2,370.00\n\n❌ <i>Condition Met: Liquidation Advised.</i>"""
        },
        {
            "name": "CAPITAL PROTECTED",
            "msg": """🛡️ <b>CAPITAL PROTECTION BREACH</b>\n\nNode: TEST_NODE\nAsset: <b>TATASTEEL</b>\n---------------------------\n💰 Buy Price: ₹150.00\n🚀 Peak Price: ₹172.00\n🛑 Exit Floor: ₹150.00\n📊 Current: ₹148.50\n\n❌ <i>Condition Met: Liquidation Advised.</i>"""
        },
        {
            "name": "PROFIT LOCKED",
            "msg": """💰 <b>PROFIT LOCK-IN VIOLATION</b>\n\nNode: TEST_NODE\nAsset: <b>HDFCBANK</b>\n---------------------------\n💰 Buy Price: ₹1,400.00\n🚀 Peak Price: ₹1,680.00\n🛑 Exit Floor: ₹1,550.00\n📊 Current: ₹1,545.00\n\n❌ <i>Condition Met: Liquidation Advised.</i>"""
        }
    ]

    print(f"Starting Standalone Broadcast (HTML MODE) to Chat {CHAT_ID}...")

    for alert in alerts:
        print(f"--- Sending {alert['name']} ---")
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": alert['msg'],
            "parse_mode": "HTML"
        }
        
        try:
            resp = requests.post(url, json=payload)
            print(f"Status: {resp.status_code}")
            if resp.status_code != 200:
                print(f"FAILED: {resp.text}")
        except Exception as e:
            print(f"FATAL ERROR: {e}")
        
        time.sleep(1)

if __name__ == "__main__":
    send_test_one_by_one()

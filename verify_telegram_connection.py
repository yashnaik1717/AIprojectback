import requests
import json

BOT_TOKEN = "8645653053:AAEu9UKXSXL2mEly6sBfy6RFebL6YA5ftZA"
CHAT_ID = "5673785873"

def verify():
    print(f"--- Telegram Connection Diagnostic ---")
    print(f"Target Bot Token: {BOT_TOKEN[:10]}...")
    print(f"Target Chat ID: {CHAT_ID}")
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
    try:
        resp = requests.get(url)
        print(f"getMe Status: {resp.status_code}")
        print(f"getMe Body: {resp.text}")
        
        if resp.status_code == 200:
            bot_info = resp.json()
            print(f"Bot Username: @{bot_info['result']['username']}")
        else:
            print("ERROR: BOT TOKEN INVALID OR EXPIRED")
            return

        # Try sending a test message
        send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": "🛠️ **DIAGNOSTIC TEST**: Can you see this message?",
            "parse_mode": "Markdown"
        }
        
        send_resp = requests.post(send_url, json=payload)
        print(f"sendMessage Status: {send_resp.status_code}")
        print(f"sendMessage Body: {send_resp.text}")
        
        if send_resp.status_code == 200:
            print("\n✅ CONNECTION SUCCESSFUL. Message should be on Telegram.")
        else:
            print("\n❌ CONNECTION FAILED. ID might be wrong or bot is blocked.")
            
    except Exception as e:
        print(f"Fatal Error: {e}")

if __name__ == "__main__":
    verify()

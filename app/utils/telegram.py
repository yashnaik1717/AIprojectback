import requests

BOT_TOKEN = "8645653053:AAEu9UKXSXL2mEly6sBfy6RFebL6YA5ftZA"   # (revoked one replace here)
CHAT_ID = "5673785873"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Telegram Error:", e)
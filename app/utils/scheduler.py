import schedule
import time
import requests
import datetime
from app.utils.telegram import send_telegram

def weekly_news_job():
    print("Executing Weekly Neural Pulse (Monday Look-ahead)...")
    try:
        # Calls the scan-news endpoint with broadcast enabled (14-day lookahead)
        requests.get("http://127.0.0.1:8000/scan-news?broadcast=true")
    except Exception as e:
        print(f"Weekly news job error: {e}")

def weekly_portfolio_job():
    print("Executing Weekly Portfolio Vault Status (Friday Recap)...")
    try:
        # Calls the new portfolio summary endpoint
        requests.get("http://127.0.0.1:8000/trigger-portfolio-summary")
    except Exception as e:
        print(f"Weekly portfolio job error: {e}")

def hourly_risk_job():
    print("Executing Hourly Risk Check (Risk Shield)...")
    try:
        # Calls the global risk scan (repeats until sold)
        requests.get("http://127.0.0.1:8000/check-global-risk")
    except Exception as e:
        print(f"Risk job error: {e}")

def monthly_rebalance_job():
    now = datetime.datetime.now()
    if now.day == 12:
        print("Executing Monthly AI Neural Scan (12th detected)...")
        try:
            # Calls logic for every user to get rebalancing suggestions and top picks
            requests.get("http://127.0.0.1:8000/trigger-automated-rebalance")
        except Exception as e:
            print(f"Monthly job error: {e}")

def run_scheduler():
    # 1. Weekly Neural Pulse (every Monday at 9:00 AM) - 14-day projection
    schedule.every().monday.at("09:00").do(weekly_news_job)

    # 2. Weekly Portfolio Vault Recap (every Friday at 6:00 PM)
    schedule.every().friday.at("18:00").do(weekly_portfolio_job)

    # 3. Hourly Risk Alerts (every 1 hour) - Continuous monitoring
    schedule.every(1).hours.do(hourly_risk_job)

    # 4. Monthly AI Neural Scan (Checks daily at 10:00 AM if it's the 12th)
    schedule.every().day.at("10:00").do(monthly_rebalance_job)

    print("--- 🛰️ AUTOMATION ENGINE ONLINE ---")
    while True:
        schedule.run_pending()
        time.sleep(60)
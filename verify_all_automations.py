import requests
import time

def verify_automation():
    base_url = "http://127.0.0.1:8000"
    
    endpoints = [
        {"name": "MONDAY: Neural Pulse (14-day)", "url": f"{base_url}/scan-news?broadcast=true"},
        {"name": "FRIDAY: Portfolio Status", "url": f"{base_url}/trigger-portfolio-summary"},
        {"name": "HOURLY: Risk Shield", "url": f"{base_url}/check-global-risk"},
        {"name": "12th DAY: AI Neural Scan", "url": f"{base_url}/trigger-automated-rebalance"}
    ]

    print("Initiating Automation Engine Verification Matrix...")

    for ep in endpoints:
        print(f"Testing {ep['name']}...")
        try:
            resp = requests.get(ep['url'], timeout=60)
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.json().get('message', 'No message')}")
        except Exception as e:
            print(f"Error testing {ep['name']}: {e}")
        
        time.sleep(3) # Wait between broadcasts

    print("\nVerification Sequence Complete. Check Telegram for 4 institutional reports.")

if __name__ == "__main__":
    verify_automation()

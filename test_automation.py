import requests

BASE_URL = "http://127.0.0.1:8000"

def test_automation():
    print("--- TESTING AUTOMATION ENDPOINTS ---")
    
    # 1. Test Weekly News
    print("\n1. Testing Weekly News Trigger...")
    r1 = requests.get(f"{BASE_URL}/scan-news?notify=true")
    print(f"Status: {r1.status_code}, Response: {r1.json().get('message')}")

    # 2. Test Hourly Risk
    print("\n2. Testing Hourly Risk Trigger...")
    r2 = requests.get(f"{BASE_URL}/check-global-risk")
    print(f"Status: {r2.status_code}, Response: {r2.json().get('message')}")

    # 3. Test Monthly Rebalance
    print("\n3. Testing Monthly Rebalance Trigger...")
    r3 = requests.get(f"{BASE_URL}/trigger-automated-rebalance")
    print(f"Status: {r3.status_code}, Response: {r3.json().get('message')}")

if __name__ == "__main__":
    test_automation()

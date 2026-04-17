import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(name, method, url, params=None):
    print(f"\n--- Testing {name} ---")
    try:
        if method == "GET":
            resp = requests.get(url, params=params)
        else:
            resp = requests.post(url, params=params)
        
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print("Response Head (300 chars):")
            print(json.dumps(resp.json(), indent=2)[:300])
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    # Test News with AI scenarios
    test_endpoint("Scan News (AI Oracle)", "GET", f"{BASE_URL}/scan-news")
    
    # Test Portfolio Growth (Real Data)
    test_endpoint("Portfolio Growth", "GET", f"{BASE_URL}/portfolio-growth", params={"user_id": 1})

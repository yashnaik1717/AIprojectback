import requests

print("--- EXECUTING API AUDIT ---")

try:
    print("1. Testing /generate-portfolio")
    r1 = requests.post("http://127.0.0.1:8000/generate-portfolio?user_id=1")
    print(f"Status Code: {r1.status_code}")
    print(f"Response: {r1.text[:300]}...")  # Truncate for terminal

    print("\n2. Testing /check-risk")
    r2 = requests.get("http://127.0.0.1:8000/check-risk?user_id=1")
    print(f"Status Code: {r2.status_code}")
    print(f"Response: {r2.text[:300]}...")

except Exception as e:
    print(f"API Error: {e}")

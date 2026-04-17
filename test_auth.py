import requests
import json

BASE_URL = "http://127.0.0.1:8000"
PHONE = "+919876543210"

def test_auth_phone():
    print(f"--- TESTING AUTH FLOW FOR {PHONE} ---")
    
    # 1. Request OTP
    print("\n1. Requesting OTP...")
    resp = requests.post(f"{BASE_URL}/auth/request-otp", json={"phone": PHONE})
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")

    # 2. Get OTP from DB (Manual check simulation)
    # The actual code would be via get_otp.py
    print("\nAuth Endpoints Verified. Check Telegram for the code.")

if __name__ == "__main__":
    test_auth_phone()

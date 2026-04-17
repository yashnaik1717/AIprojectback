import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "app")))

from app.db.database import engine
from sqlalchemy import text

def get_tester_otp_phone():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT otp_code FROM users WHERE phone='+919876543210'"))
        row = result.fetchone()
        if row:
            print(f"OTP_IS: {row[0]}")
        else:
            print("USER_NOT_FOUND")

if __name__ == "__main__":
    get_tester_otp_phone()

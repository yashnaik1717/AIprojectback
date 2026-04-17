import sys
import os

# Append 'app' directory to path to resolve imports locally
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "app")))

from app.db.database import SessionLocal, engine
from sqlalchemy import text

def test_db():
    print("Testing DB connection...")
    try:
        db = SessionLocal()
        users = db.execute(text("SELECT * FROM users LIMIT 1")).fetchall()
        print(f"Users fetch success: {users}")
        
        portfolios = db.execute(text("SELECT * FROM portfolio LIMIT 5")).fetchall()
        print("Portfolio Schema and initial fetch success.")
        for row in portfolios:
            print(f"Row values: {row}")
            
    except Exception as e:
        print(f"DB Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_db()

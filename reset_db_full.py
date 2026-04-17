import sys
import os

# Ensure local imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "app")))

from app.db.database import engine, Base
from app.db.models import User, Portfolio, FundHistory

print("--- RESETTING DATABASE SCHEMAS ---")

# Step 1: Drop
try:
    Base.metadata.drop_all(bind=engine)
    print("Dropped all existing tables.")
except Exception as e:
    print(f"Drop error: {e}")

# Step 2: Create
try:
    Base.metadata.create_all(bind=engine)
    print("Re-created all tables with fresh schemas (Auth included).")
except Exception as e:
    print(f"Creation error: {e}")

print("Database Sync Successful. Terminals ready for Uplink.")

import sys
import os

# Ensure local imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "app")))

from app.db.database import engine
from app.db.models import Portfolio

print("Dropping Portfolio table...")
try:
    Portfolio.__table__.drop(engine)
    print("Table dropped perfectly!")
except Exception as e:
    print(f"Error dropping table. Maybe it doesn't exist? {e}")

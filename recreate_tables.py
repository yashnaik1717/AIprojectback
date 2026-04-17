import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "app")))

from app.db.database import engine, Base
from app.db.models import *

Base.metadata.create_all(bind=engine)
print("Successfully recreated Database schemas with the new score/rsi columns!")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

import os

# Use environment variable for production (Supabase/Neon), fallback to local for dev
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Yash1717@localhost:5432/AI_agent")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()
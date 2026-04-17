import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Yash1717@localhost:5432/AI_agent")
engine = create_engine(DATABASE_URL)

def add_columns():
    cols = [
        ("highest_price", "DOUBLE PRECISION DEFAULT 0.0"),
        ("trailing_sl_percent", "DOUBLE PRECISION DEFAULT 5.0"),
        ("target_price", "DOUBLE PRECISION")
    ]
    
    with engine.connect() as conn:
        for col_name, col_type in cols:
            try:
                print(f"Adding column {col_name}...")
                conn.execute(text(f"ALTER TABLE portfolio ADD COLUMN {col_name} {col_type};"))
                conn.commit()
                print(f"Column {col_name} added successfully.")
            except Exception as e:
                print(f"Error adding {col_name}: {e}")
                conn.rollback()

if __name__ == "__main__":
    add_columns()

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in .env file")

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        print("PostgreSQL connection successful! - database.py:16")
except Exception as e:
    print("Error: - database.py:18", e)
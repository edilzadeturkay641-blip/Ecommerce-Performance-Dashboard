from sqlalchemy import create_engine

DB_USER = "postgres"
DB_PASSWORD = "Turk!19971997"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "ecommerce_dashboard"

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

try:
    with engine.connect() as conn:
        print("PostgreSQL connection successful! - database.py:15")
except Exception as e:
    print("Error: - database.py:17", e)
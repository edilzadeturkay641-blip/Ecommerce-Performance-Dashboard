import pandas as pd
from database import engine

# CSV-ni oxu
df = pd.read_csv("data/orders.csv")

# Tarixi datetime formatına çevir
df["order_date"] = pd.to_datetime(df["order_date"])

# PostgreSQL-ə yaz
df.to_sql(
    "orders",
    engine,
    if_exists="replace",
    index=False
)

print("Orders table created successfully! - load_orders.py:18")
print(df.head())
import pandas as pd
from database import engine

df = pd.read_json("data/customers.json")

df["registration_date"] = pd.to_datetime(df["registration_date"])

df.to_sql(
    "customers",
    engine,
    if_exists="replace",
    index=False
)

print("Customers table created successfully! - load_customers.py:15")
print(df.head())
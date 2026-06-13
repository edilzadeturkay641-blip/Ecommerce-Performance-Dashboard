import pandas as pd
from database import engine

df = pd.read_json("data/reviews.json")

df["review_date"] = pd.to_datetime(df["review_date"])

df.to_sql(
    "reviews",
    engine,
    if_exists="replace",
    index=False
)

print("Reviews table created successfully! - load_reviews.py:15")
print(df.head())
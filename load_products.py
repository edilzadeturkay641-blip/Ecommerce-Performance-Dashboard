import pandas as pd
import requests
from database import engine

API_URL = "https://fakestoreapi.com/products"

response = requests.get(API_URL)
response.raise_for_status()

products = response.json()

df = pd.DataFrame(products)

df["rating_rate"] = df["rating"].apply(lambda x: x["rate"])
df["rating_count"] = df["rating"].apply(lambda x: x["count"])

df = df.drop(columns=["rating"])

df = df.rename(columns={
    "id": "product_id",
    "title": "product_name"
})

df = df[[
    "product_id",
    "product_name",
    "price",
    "description",
    "category",
    "image",
    "rating_rate",
    "rating_count"
]]

df.to_sql("products", engine, if_exists="replace", index=False)

print("Products table created successfully! - load_products.py:37")
print(df.head())
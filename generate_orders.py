import pandas as pd
import random
from datetime import datetime, timedelta

orders = []

for i in range(1, 1001):
    orders.append({
        "order_id": i,
        "customer_id": random.randint(100, 500),
        "order_date": (
            datetime(2026, 1, 1)
            + timedelta(days=random.randint(0, 180))
        ).strftime("%Y-%m-%d"),
        "product_id": random.randint(1, 20),
        "quantity": random.randint(1, 5)
    })

df = pd.DataFrame(orders)

df.to_csv("data/orders.csv", index=False)

print("1000 orders generated - generate_orders.py:23")
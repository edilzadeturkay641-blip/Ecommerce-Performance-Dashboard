import json
import random
from datetime import datetime, timedelta

reviews = []

for review_id in range(1, 2001):

    reviews.append({
        "review_id": review_id,

        "customer_id": random.randint(100, 500),

        "product_id": random.randint(1, 20),

        "rating": random.randint(1, 5),

        "review_date": (
            datetime(2024, 1, 1)
            + timedelta(days=random.randint(0, 180))
        ).strftime("%Y-%m-%d")
    })

with open("data/reviews.json", "w") as f:
    json.dump(reviews, f, indent=4)

print("reviews.json generated successfully - generate_reviews.py:27")
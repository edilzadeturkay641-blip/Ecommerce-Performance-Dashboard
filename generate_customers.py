import random
import json
from datetime import datetime, timedelta

cities = [
    "Baku",
    "Ganja",
    "Sumgait",
    "Mingachevir",
    "Shaki",
    "Lankaran"
]

customers = []

for customer_id in range(100, 501):

    customers.append({
        "customer_id": customer_id,
        "name": f"Customer_{customer_id}",
        "city": random.choice(cities),
        "gender": random.choice(["Male", "Female"]),
        "age": random.randint(18, 65),

        "membership_type": random.choice([
            "Standard",
            "Premium",
            "VIP"
        ]),

        "registration_date": (
            datetime(2025, 1, 1)
            + timedelta(days=random.randint(0, 900))
        ).strftime("%Y-%m-%d")
    })

with open("data/customers.json", "w") as f:
    json.dump(customers, f, indent=4)

print("customers.json generated successfully - generate_customers.py:40")
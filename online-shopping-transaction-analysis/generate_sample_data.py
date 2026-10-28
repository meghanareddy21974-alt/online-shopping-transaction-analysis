"""Create data/sample_transactions.csv with realistic random orders."""
import csv
import os
import random
from datetime import date, timedelta

random.seed(42)
PRODUCTS = {
    "Electronics": [("Wireless Earbuds", 59), ("Smartphone Case", 12), ("Power Bank", 28), ("Smart Watch", 120), ("USB-C Cable", 8)],
    "Fashion": [("Running Shoes", 70), ("Denim Jacket", 55), ("Cotton T-Shirt", 15), ("Backpack", 35)],
    "Home": [("Desk Lamp", 25), ("Coffee Maker", 65), ("Bed Sheet Set", 40), ("Air Fryer", 90)],
    "Books": [("Python Handbook", 30), ("Novel Bestseller", 14), ("Cookbook", 22)],
    "Beauty": [("Face Serum", 26), ("Perfume", 48), ("Hair Dryer", 38)],
}
PAYMENTS = ["Credit Card", "Debit Card", "UPI", "PayPal", "Cash on Delivery"]
start, end = date(2025, 1, 1), date(2026, 10, 26)
days = (end - start).days

rows = []
for i in range(1, 2501):
    cat = random.choices(list(PRODUCTS), weights=[30, 25, 20, 10, 15])[0]
    product, price = random.choice(PRODUCTS[cat])
    rows.append({
        "order_id": f"ORD{i:05d}",
        "order_date": (start + timedelta(days=random.randint(0, days))).isoformat(),
        "customer_id": f"CUST{random.randint(1, 300):04d}",
        "product": product, "category": cat,
        "quantity": random.choices([1, 2, 3, 4], weights=[60, 25, 10, 5])[0],
        "unit_price": round(price * random.uniform(0.9, 1.1), 2),
        "payment_method": random.choices(PAYMENTS, weights=[30, 20, 25, 10, 15])[0],
        "status": random.choices(["Completed", "Returned", "Cancelled"], weights=[86, 8, 6])[0],
    })
rows.sort(key=lambda r: r["order_date"])

os.makedirs("data", exist_ok=True)
with open("data/sample_transactions.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print(f"Wrote {len(rows)} rows to data/sample_transactions.csv")

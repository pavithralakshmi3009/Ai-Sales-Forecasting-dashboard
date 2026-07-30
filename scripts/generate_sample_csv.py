"""
Generate realistic sample sales data for the AI Sales Forecasting Dashboard.

Business Rules:
- Total  = Unit Price × Quantity
- Cost   = Cost Price × Quantity
- Profit = Total − Cost
- Products are mapped to fixed categories
- Prices reflect real-world Indian retail pricing
"""

import csv
import random
from datetime import datetime, timedelta

# -------------------------------------------------------
# Realistic Product Catalog: Product → (Category, UnitPrice, CostPrice)
# Prices in ₹ — realistic Indian retail prices
# -------------------------------------------------------
PRODUCT_CATALOG = {
    # Electronics
    "Samsung 27\" Monitor":    ("Electronics",  18999.00, 14500.00),
    "LG UltraWide Monitor":   ("Electronics",  24999.00, 19200.00),
    "Logitech Webcam C920":   ("Electronics",   7499.00,  5600.00),
    "Smart Watch Pro":         ("Electronics",  12999.00,  9100.00),

    # Laptops
    "MacBook Air M2":         ("Electronics",  99999.00, 82000.00),
    "Dell XPS 15":            ("Electronics",  89999.00, 72000.00),
    "ThinkPad X1 Carbon":     ("Electronics",  74999.00, 60000.00),
    "HP Pavilion 15":         ("Electronics",  54999.00, 44000.00),

    # Mobile
    "iPhone 15":              ("Electronics",  79999.00, 66000.00),
    "Samsung Galaxy S24":     ("Electronics",  74999.00, 58000.00),
    "Google Pixel 8":         ("Electronics",  52999.00, 42000.00),

    # Tablets
    "iPad Pro 12.9\"":        ("Electronics",  112999.00, 90000.00),
    "Samsung Galaxy Tab S9":  ("Electronics",   74999.00, 58000.00),

    # Accessories
    "Sony WH-1000XM5":       ("Accessories",  29999.00, 22000.00),
    "Mechanical Keyboard":    ("Accessories",   4999.00,  3200.00),
    "Logitech MX Master 3S":  ("Accessories",   8999.00,  6500.00),
    "JBL Flip 6 Speaker":     ("Accessories",   9999.00,  7200.00),
    "USB-C Hub Adapter":      ("Accessories",   2499.00,  1600.00),

    # Office Equipment
    "HP LaserJet Pro":        ("Office Equipment", 21999.00, 16500.00),
    "Epson EcoTank L3250":    ("Office Equipment", 13999.00, 10500.00),
}

CUSTOMERS = [
    "Reliance Digital", "Croma Electronics", "Vijay Sales", "Amazon India",
    "Flipkart Wholesale", "TCS Procurement", "Infosys IT", "Wipro Ltd",
    "HCL Technologies", "Tech Mahindra",
]


def generate_csv(filename="sample_sales_data.csv", num_records=60):
    """Generate exactly `num_records` realistic sales records."""
    products = list(PRODUCT_CATALOG.keys())
    # Dates span Jan 2024 – Dec 2024
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    date_range_days = (end_date - start_date).days

    random.seed(42)  # Deterministic for reproducibility

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Date", "Invoice Number", "Customer Name",
            "Product", "Category", "Quantity", "Price", "Total", "Profit"
        ])

        used_invoices = set()
        for _ in range(num_records):
            # Random date across 2024
            days_offset = random.randint(0, date_range_days)
            date = (start_date + timedelta(days=days_offset)).strftime("%Y-%m-%d")

            # Product selection
            product = random.choice(products)
            category, unit_price, cost_price = PRODUCT_CATALOG[product]

            # Quantity: 1–5 for expensive items, 1–10 for cheaper ones
            max_qty = 3 if unit_price > 50000 else (5 if unit_price > 10000 else 10)
            quantity = random.randint(1, max_qty)

            # Business calculations
            total = round(unit_price * quantity, 2)
            cost = round(cost_price * quantity, 2)
            profit = round(total - cost, 2)

            # Unique invoice number
            while True:
                inv = f"INV-{random.randint(100000, 999999)}"
                if inv not in used_invoices:
                    used_invoices.add(inv)
                    break

            customer = random.choice(CUSTOMERS)

            writer.writerow([
                date, inv, customer,
                product, category, quantity, unit_price, total, profit
            ])

    print(f"Generated {num_records} records in {filename}")


if __name__ == "__main__":
    generate_csv()

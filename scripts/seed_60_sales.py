import os
import sys
import random
from datetime import datetime, timedelta

# Ensure api directory is in path
sys.path.insert(0, os.path.abspath('api'))

from _services.database import get_db_connection, insert_sale, save_dataset_rows

PRODUCTS_BY_CATEGORY = {
    'Electronics': [
        ('Pro Laptop 15"', 1200.00),
        ('Ultra Smartphone 5G', 899.00),
        ('Noise-Canceling Headphones', 199.50),
        ('4K Ultra HD Monitor', 450.00),
        ('Fitness Smartwatch', 149.00),
        ('Wireless Mechanical Keyboard', 129.99),
        ('Ergonomic Wireless Mouse', 59.99),
        ('USB-C Thunderbolt Dock', 180.00)
    ],
    'Software': [
        ('Enterprise Cloud License', 2500.00),
        ('AI Sales Assistant Pro', 499.00),
        ('Cybersecurity Suite', 799.00),
        ('Data Analytics Subscription', 299.00),
        ('CRM Unlimited Access', 1200.00)
    ],
    'Office Supplies': [
        ('Ergonomic Mesh Chair', 350.00),
        ('Electric Standing Desk', 650.00),
        ('Dual Monitor Steel Arm', 89.00),
        ('Desk Cable Management Kit', 25.00),
        ('Acoustic Desk Divider', 110.00)
    ],
    'Services': [
        ('Annual IT Maintenance', 1500.00),
        ('Custom API Integration', 3000.00),
        ('Cloud Migration Consultancy', 4500.00),
        ('Staff Training Workshop', 1200.00)
    ]
}

def seed_database():
    print("Connecting to Supabase PostgreSQL database...")
    start_date = datetime(2025, 8, 1)
    
    sales_data = []
    
    for i in range(60):
        # Generate random date over the last 12 months
        random_days = random.randint(0, 360)
        sale_date = (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")
        
        category = random.choice(list(PRODUCTS_BY_CATEGORY.keys()))
        product, base_price = random.choice(PRODUCTS_BY_CATEGORY[category])
        
        # Add slight variation to price
        price = round(base_price * random.uniform(0.95, 1.05), 2)
        quantity = random.randint(1, 15)
        total = round(quantity * price, 2)
        
        # Profit margin between 20% and 40%
        profit_margin = random.uniform(0.20, 0.40)
        profit = round(total * profit_margin, 2)
        
        sales_data.append((sale_date, product, category, quantity, price, total, profit))

    # Insert into database
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            # Clear existing sales table if wanted, or append
            print("Inserting 60 random sales records...")
            cursor.executemany(
                """
                INSERT INTO sales (date, product, category, quantity, price, total, profit)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                sales_data
            )
        conn.commit()
    
    print(f"Successfully inserted {len(sales_data)} sales records into Supabase database!")

    # Also seed 60 monthly dataset rows for sales forecasting ML model
    dataset_rows = []
    base_sales = 15000.0
    for month in range(1, 61):
        trend = base_sales + (month * 1800.0)
        seasonality = random.uniform(-3000, 3500)
        monthly_sales = round(trend + seasonality, 2)
        dataset_rows.append({'month': month, 'sales': monthly_sales})
    
    save_dataset_rows(dataset_rows)
    print("Successfully populated 60 monthly forecasting dataset rows!")

if __name__ == '__main__':
    seed_database()

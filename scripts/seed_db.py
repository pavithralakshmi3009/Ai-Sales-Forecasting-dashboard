import os
import sys
import csv
import random
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

# Add project root to sys.path so we can import _services
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "api"))

from _services.database import get_db_connection, init_db
from _services.utils import hash_password

def seed_database(csv_path):
    print("Initializing database tables...")
    init_db()

    print(f"Reading sample data from {csv_path}...")
    if not os.path.exists(csv_path):
        print(f"File {csv_path} not found. Please generate it first.")
        return

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print("CSV is empty.")
        return

    print("Inserting data into 'sales' table...")
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            # Clear existing data to avoid duplication during seed
            cursor.execute("TRUNCATE TABLE sales RESTART IDENTITY CASCADE")
            cursor.execute("TRUNCATE TABLE dataset_rows RESTART IDENTITY CASCADE")
            
            for row in rows:
                cursor.execute(
                    """
                    INSERT INTO sales (date, product, category, quantity, price, total, profit)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        row["Date"],
                        row["Product"],
                        row["Category"],
                        int(row["Quantity"]),
                        float(row["Price"]),
                        float(row["Total"]),
                        float(row["Profit"])
                    )
                )

            # Generate dataset_rows for ML (Monthly aggregated sales)
            # We'll aggregate by Month (1 to 12) for simplicity, or relative months
            # Actually, let's aggregate the inserted data into month groups
            cursor.execute("SELECT date, total FROM sales")
            sales_data = cursor.fetchall()
            
            monthly_sales = {}
            for date_str, total in sales_data:
                # Group by YYYY-MM
                try:
                    dt = datetime.strptime(date_str, "%Y-%m-%d")
                    # Map to a continuous month index for Linear Regression
                    # Let's say Jan 2023 = Month 1, Feb 2023 = Month 2, etc.
                    month_index = (dt.year - 2023) * 12 + dt.month
                    if month_index > 0:
                        monthly_sales[month_index] = monthly_sales.get(month_index, 0) + float(total)
                except ValueError:
                    pass
            
            for month, total_sales in sorted(monthly_sales.items()):
                cursor.execute(
                    "INSERT INTO dataset_rows (month, sales) VALUES (%s, %s)",
                    (month, total_sales)
                )
                
        conn.commit()
    print("Database seeded successfully!")

if __name__ == "__main__":
    csv_file = BASE_DIR / "sample_sales_data.csv"
    if not os.path.exists(csv_file):
        # We also generate it directly if not found
        from generate_sample_csv import generate_csv
        generate_csv(str(csv_file), 60)
        
    seed_database(str(csv_file))

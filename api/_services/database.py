"""
Centralized Database Module for Supabase PostgreSQL.

Provides:
- Connection management optimized for Vercel Serverless Functions
- Automatic SSL enforcement
- Automatic Supabase pooler port conversion (5432 → 6543)
- Safe error handling and logging (never exposes secrets)
- Context manager for connection lifecycle
- All CRUD operations for the application
"""
import os
import logging
import psycopg2
import psycopg2.extras
from contextlib import contextmanager
from datetime import datetime
from _services.config import DATABASE_URL
from _services.utils import hash_password, verify_hashed_password

logger = logging.getLogger(__name__)


def _get_database_url():
    """
    Parse and configure DATABASE_URL for Serverless/Supabase compatibility.

    - Strips accidental brackets from password if user pasted [password]
    - Converts postgres:// to postgresql:// (required by psycopg2)
    - Converts Supabase direct port 5432 to pooler port 6543 (IPv4 fix)
    - Appends sslmode=require if missing
    """
    db_url = os.environ.get("DATABASE_URL") or DATABASE_URL
    if not db_url:
        raise RuntimeError(
            "DATABASE_URL is not set. "
            "Configure it in your environment or .env file."
        )

    # Strip accidental brackets around password (e.g. :[password]@ -> :password@)
    import re
    db_url = re.sub(r':\[([^\]]+)\]@', r':\1@', db_url)

    # Fix URI scheme
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    # Convert Supabase direct port 5432 to pooler port 6543 (IPv4 fix for Vercel)
    if ":5432" in db_url and "supabase" in db_url:
        db_url = db_url.replace(":5432", ":6543")

    # Ensure SSL
    if "sslmode=" not in db_url:
        separator = "&" if "?" in db_url else "?"
        db_url = f"{db_url}{separator}sslmode=require"

    return db_url


@contextmanager
def get_db_connection():
    """
    Context manager that creates a fresh psycopg2 connection per request.

    This is the correct pattern for Vercel Serverless Functions:
    - Each invocation gets a fresh connection
    - No stale pool references across cold starts
    - Connection is always closed after use
    """
    conn = None
    try:
        conn = psycopg2.connect(_get_database_url(), connect_timeout=10)
        yield conn
    except psycopg2.OperationalError as e:
        logger.error(f"Database connection failed: {type(e).__name__} - {str(e)}")
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        raise RuntimeError("Database connection failed. Please try again later.") from e
    except psycopg2.Error as e:
        logger.error(f"Database error: {type(e).__name__}: {e.pgerror or e}")
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        raise RuntimeError("A database error occurred.") from e
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


# ----------------------------------------
# Database Initialization
# ----------------------------------------
def init_db():
    """Create all required tables if they do not exist and seed default admin user."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            # 1. Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users(
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL
                )
            """)

            # 2. Sales table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sales(
                    id SERIAL PRIMARY KEY,
                    date TEXT NOT NULL,
                    product TEXT NOT NULL,
                    category TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price DOUBLE PRECISION NOT NULL,
                    total DOUBLE PRECISION NOT NULL,
                    profit DOUBLE PRECISION NOT NULL
                )
            """)

            # 3. Dataset rows table (Month/Sales from CSV uploads)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dataset_rows(
                    id SERIAL PRIMARY KEY,
                    month INTEGER NOT NULL,
                    sales DOUBLE PRECISION NOT NULL,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 4. Uploaded datasets metadata
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS uploaded_datasets(
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    record_count INTEGER NOT NULL
                )
            """)

            # 5. Prediction history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prediction_history(
                    id SERIAL PRIMARY KEY,
                    month INTEGER NOT NULL,
                    predicted_sales DOUBLE PRECISION NOT NULL,
                    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 6. Model metadata
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS model_metadata(
                    id SERIAL PRIMARY KEY,
                    accuracy DOUBLE PRECISION NOT NULL,
                    algorithm VARCHAR(100) NOT NULL,
                    training_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    dataset_size INTEGER NOT NULL
                )
            """)

            # 7. Training Logs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS training_logs(
                    id SERIAL PRIMARY KEY,
                    r2_score DOUBLE PRECISION,
                    mae DOUBLE PRECISION,
                    rmse DOUBLE PRECISION,
                    mse DOUBLE PRECISION,
                    training_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'TRAINED'
                )
            """)

            # 8. Forecast History
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS forecast_history(
                    id SERIAL PRIMARY KEY,
                    forecast_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    forecast_data JSONB NOT NULL
                )
            """)

            # Seed default admin user (hashed password)
            cursor.execute("SELECT id FROM users WHERE username = %s", ('admin',))
            if not cursor.fetchone():
                hashed_pw = hash_password('admin123')
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (%s, %s)",
                    ('admin', hashed_pw)
                )
                logger.info("Seeded default admin user.")

        conn.commit()
        logger.info("Database tables initialized successfully.")


# ----------------------------------------
# User Authentication
# ----------------------------------------
def get_user_by_username(username):
    """Return user dict with id, username, password (hashed) or None."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, username, password FROM users WHERE username = %s",
                (username,)
            )
            row = cursor.fetchone()
            if row:
                return {"id": row[0], "username": row[1], "password": row[2]}
            return None


def check_user_credentials(username, password):
    """Validate username/password. Supports both hashed and legacy plaintext passwords."""
    user = get_user_by_username(username)
    if not user:
        return False

    stored_pw = user["password"]

    # Support hashed passwords (werkzeug format)
    if stored_pw.startswith(("pbkdf2:", "scrypt:")):
        return verify_hashed_password(stored_pw, password)

    # Fallback: legacy plaintext comparison
    return stored_pw == password


# ----------------------------------------
# Sales CRUD Operations
# ----------------------------------------
def insert_sale(date, product, category, quantity, price, total, profit):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO sales (date, product, category, quantity, price, total, profit)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (date, product, category, quantity, price, total, profit)
            )
        conn.commit()


def view_sales(limit=None):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            if limit:
                cursor.execute(
                    "SELECT id, date, product, category, quantity, price, total, profit "
                    "FROM sales ORDER BY id DESC LIMIT %s", (limit,)
                )
            else:
                cursor.execute(
                    "SELECT id, date, product, category, quantity, price, total, profit "
                    "FROM sales ORDER BY id ASC"
                )
            rows = cursor.fetchall()
            return [
                {
                    'id': r[0],
                    'date': r[1],
                    'product': r[2],
                    'category': r[3],
                    'quantity': r[4],
                    'price': r[5],
                    'total': r[6],
                    'profit': r[7]
                }
                for r in rows
            ]


def search_sale(product):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, date, product, category, quantity, price, total, profit "
                "FROM sales WHERE product ILIKE %s ORDER BY id ASC",
                ('%' + product + '%',)
            )
            rows = cursor.fetchall()
            return [
                {
                    'id': r[0],
                    'date': r[1],
                    'product': r[2],
                    'category': r[3],
                    'quantity': r[4],
                    'price': r[5],
                    'total': r[6],
                    'profit': r[7]
                }
                for r in rows
            ]


def update_sale(id, date, product, category, quantity, price, total, profit):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE sales
                SET date=%s, product=%s, category=%s, quantity=%s,
                    price=%s, total=%s, profit=%s
                WHERE id=%s
                """,
                (date, product, category, quantity, price, total, profit, id)
            )
        conn.commit()


def delete_sale(id):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM sales WHERE id=%s", (id,))
        conn.commit()


# ----------------------------------------
# Dataset Rows (CSV upload storage)
# ----------------------------------------
def save_dataset_rows(rows):
    """Replace all existing dataset rows with new ones."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM dataset_rows")
            for row in rows:
                cursor.execute(
                    "INSERT INTO dataset_rows (month, sales) VALUES (%s, %s)",
                    (int(row['month']), float(row['sales']))
                )
        conn.commit()
        logger.info(f"Saved {len(rows)} dataset rows to database.")


def get_dataset_rows():
    """Fetch all dataset rows, ordered by month."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT month, sales FROM dataset_rows ORDER BY month ASC")
            rows = cursor.fetchall()
            return [{"Month": r[0], "Sales": r[1]} for r in rows]


# ----------------------------------------
# Logs & Metadata
# ----------------------------------------
def log_uploaded_dataset(filename, record_count):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO uploaded_datasets (filename, record_count) VALUES (%s, %s)",
                (filename, record_count)
            )
        conn.commit()


def log_prediction(month, predicted_sales):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO prediction_history (month, predicted_sales) VALUES (%s, %s)",
                (month, predicted_sales)
            )
        conn.commit()


def save_model_metadata(accuracy, algorithm, dataset_size):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO model_metadata (accuracy, algorithm, training_date, dataset_size)
                VALUES (%s, %s, %s, %s)
                """,
                (accuracy, algorithm, datetime.now(), dataset_size)
            )
        conn.commit()


def get_latest_model_metadata():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT accuracy, algorithm, training_date, dataset_size "
                "FROM model_metadata ORDER BY id DESC LIMIT 1"
            )
            row = cursor.fetchone()
            if row:
                t_date = row[2]
                if isinstance(t_date, str):
                    try:
                        dt = datetime.fromisoformat(t_date.replace('Z', '+00:00'))
                        t_date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        t_date_str = t_date
                else:
                    t_date_str = t_date.strftime("%Y-%m-%d %H:%M:%S") if t_date else "Unknown"

                return {
                    "accuracy": round(float(row[0]), 4),
                    "algorithm": row[1],
                    "training_date": t_date_str,
                    "dataset_size": row[3]
                }
            return None

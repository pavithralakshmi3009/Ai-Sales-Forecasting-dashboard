import os
import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = os.environ.get("MODEL_PATH", BASE_DIR / "models" / "sales_model.pkl")
MODEL_JSON_PATH = os.environ.get("MODEL_JSON_PATH", BASE_DIR / "models" / "sales_model.json")

# Secret Keys — use a safe default for local development only
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-fallback-secret-key-change-in-production')
JWT_SECRET = os.environ.get("JWT_SECRET") or SECRET_KEY

# Environment
FLASK_ENV = os.environ.get("FLASK_ENV", "production")

# Database & Supabase Configuration
DEFAULT_SUPABASE_URL = "postgresql://postgres.uwvlmberqqjryhewsvds:Paviakash37@aws-1-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require"
DATABASE_URL = os.environ.get("DATABASE_URL") or DEFAULT_SUPABASE_URL
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://uwvlmberqqjryhewsvds.supabase.co")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not DATABASE_URL:
    logger.warning(
        "DATABASE_URL environment variable is not set. "
        "Configure it in environment variables or .env file."
    )

# CORS Origins
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    re.compile(r"^https://.*\.vercel\.app$")
]
if os.environ.get("ALLOWED_ORIGINS"):
    CORS_ORIGINS.extend(os.environ.get("ALLOWED_ORIGINS").split(","))

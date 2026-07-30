import os
import sys
import logging
from flask import Flask
from flask_cors import CORS

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure logging before any other imports
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Ensure the api directory is in sys.path for _services/_routes imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _services.config import SECRET_KEY, CORS_ORIGINS, DATABASE_URL

# Startup Validation
if not DATABASE_URL:
    logger.critical("DATABASE_URL is missing. Application cannot start.")
    sys.exit(1)
if not DATABASE_URL.startswith("postgres://") and not DATABASE_URL.startswith("postgresql://"):
    logger.critical("DATABASE_URL is malformed. Must be a PostgreSQL URI.")
    sys.exit(1)

from _routes.auth import auth_bp
from _routes.dashboard import dashboard_bp
from _routes.health import health_bp
from _routes.sales import sales_bp
from _routes.upload import upload_bp
from _routes.history import history_bp
from _routes.predict import predict_bp

app = Flask(__name__)
app.secret_key = SECRET_KEY
CORS(app, supports_credentials=True, origins=CORS_ORIGINS)

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(health_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(history_bp)
app.register_blueprint(predict_bp)

# Initialize database tables on first load
try:
    from _services.database import init_db
    init_db()
    logger.info("Database initialized successfully on startup.")
except Exception as e:
    logger.error(f"Database initialization failed: {e}")

if __name__ == '__main__':
    app.run(debug=True, port=5000)

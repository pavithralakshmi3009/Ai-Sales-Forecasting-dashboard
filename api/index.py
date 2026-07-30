import os
import sys
import logging
from flask import Flask, jsonify
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

from _services.config import SECRET_KEY, CORS_ORIGINS

from _routes.auth import auth_bp
from _routes.dashboard import dashboard_bp
from _routes.health import health_bp
from _routes.sales import sales_bp
from _routes.upload import upload_bp
from _routes.history import history_bp
from _routes.predict import predict_bp

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Ensure CORS supports Vercel preview/production domains and localhost
CORS(app, supports_credentials=True, origins=CORS_ORIGINS)

# Global Error Handlers to guarantee JSON responses (never HTML 500)
@app.errorhandler(500)
def handle_internal_server_error(e):
    logger.error(f"Internal Server Error: {e}")
    db_url = os.environ.get("DATABASE_URL")
    err_msg = str(e)
    if not db_url:
        err_msg = "DATABASE_URL environment variable is missing on Vercel. Please set DATABASE_URL in Vercel project settings."
    return jsonify({
        'success': False,
        'message': err_msg,
        'error': err_msg
    }), 500

@app.errorhandler(404)
def handle_not_found(e):
    return jsonify({
        'success': False,
        'message': 'Requested API route not found',
        'error': 'Not Found'
    }), 404

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(health_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(history_bp)
app.register_blueprint(predict_bp)

# Lazy Database Initialization flag for Serverless Functions
_db_initialized = False

@app.before_request
def init_db_once():
    global _db_initialized
    if not _db_initialized:
        db_url = os.environ.get("DATABASE_URL")
        if db_url:
            try:
                from _services.database import init_db
                init_db()
                _db_initialized = True
                logger.info("Database tables initialized successfully.")
            except Exception as e:
                logger.error(f"Database initialization failed: {e}")
        else:
            logger.warning("DATABASE_URL is not configured in environment variables.")

if __name__ == '__main__':
    app.run(debug=True, port=5000)

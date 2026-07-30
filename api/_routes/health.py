# pyrefly: ignore [missing-import]
from flask import Blueprint
import os
import sys
import logging
from flask import jsonify

# Removed sys.path modification to avoid ModuleNotFoundError on Vercel

from _services.config import CORS_ORIGINS
from _services.database import get_db_connection

logger = logging.getLogger(__name__)

health_bp = Blueprint("health", __name__)


@health_bp.route('/api/health', methods=['GET'])
@health_bp.route('/health', methods=['GET'])
def health():
    db_status = "unknown"
    db_error = None
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        db_status = "connected"
    except Exception as e:
        db_status = "disconnected"
        db_error = str(e)
        if hasattr(e, '__cause__') and e.__cause__:
            db_error += f" | Cause: {str(e.__cause__)}"
        logger.error(f"Health check DB error: {db_error}")

    status_code = 200 if db_status == "connected" else 500
    return jsonify({
        'status': 'ok' if db_status == 'connected' else 'error',
        'message': 'Backend running successfully',
        'database': db_status,
        'database_error': db_error
    }), status_code

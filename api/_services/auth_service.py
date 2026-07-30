import jwt
import logging
from datetime import datetime, timezone, timedelta
from functools import wraps
from flask import request, jsonify
from _services.config import JWT_SECRET

logger = logging.getLogger(__name__)


def _get_jwt_secret():
    """Get JWT_SECRET from config variables."""
    return JWT_SECRET


def generate_token(username):
    """Generate a JWT token for the given username. Expires in 24 hours."""
    secret = _get_jwt_secret()
    payload = {
        "sub": username,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token


def verify_token(token):
    """
    Decode and verify a JWT token.
    Returns the payload dict on success, None on failure.
    """
    secret = _get_jwt_secret()
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        logger.debug("JWT token has expired.")
        return None
    except jwt.InvalidTokenError as e:
        logger.debug(f"Invalid JWT token: {e}")
        return None


def get_token_from_request():
    """Extract the Bearer token from the Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None


def require_auth(f):
    """
    Decorator that protects a route with JWT authentication.
    Returns 401 JSON response if the token is missing or invalid.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_request()
        if not token:
            return jsonify({"error": "Unauthorized — no token provided"}), 401

        payload = verify_token(token)
        if not payload:
            return jsonify({"error": "Unauthorized — invalid or expired token"}), 401

        # Attach username to request context for downstream use
        request.auth_user = payload.get("sub")
        return f(*args, **kwargs)

    return decorated

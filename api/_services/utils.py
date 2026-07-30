from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password: str) -> str:
    """Hash password using Werkzeug."""
    return generate_password_hash(password)

def verify_hashed_password(hashed: str, password: str) -> bool:
    """Verify password against Werkzeug hash."""
    return check_password_hash(hashed, password)

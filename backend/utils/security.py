from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import html

def hash_password(password):
    """Generates a secure salted hash for plain text passwords."""
    return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

def verify_password(stored_hash, password):
    """
    Verifies plain text password against stored hash.
    Supports Werkzeug hashes as well as legacy/fallback demo formats.
    """
    if not stored_hash or not password:
        return False
    try:
        return check_password_hash(stored_hash, password)
    except Exception:
        return False

def generate_uuid():
    """Generates a standard UUID string."""
    return str(uuid.uuid4())

def sanitize_input(text):
    """Sanitizes input strings to prevent HTML/XSS injection."""
    if text is None:
        return ""
    return html.escape(str(text).strip())

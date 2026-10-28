import secrets
from datetime import datetime, timedelta
from db import execute_query
from utils.security import hash_password, verify_password, generate_uuid
from utils.validators import validate_registration_payload, validate_mobile, validate_email
from services.audit_service import log_audit_event
from config import Config

def register_user(payload, ip_address=None, user_agent=None):
    is_valid, errors, sanitized = validate_registration_payload(payload)
    if not is_valid:
        return False, {"message": errors[0], "errors": errors, "error_code": "VALIDATION_FAILED"}, 422

    mobile = sanitized['mobile']
    email = sanitized['email']
    full_name = sanitized['full_name']
    role_name = sanitized['role_name']
    preferred_lang = sanitized['preferred_language']

    # 1. Check duplicate mobile
    existing_mob = execute_query("SELECT id FROM users WHERE mobile = %s", (mobile,), fetchone=True)
    if existing_mob:
        return False, {"message": "Mobile number is already registered.", "error_code": "AUTH_DUPLICATE_MOBILE"}, 409

    # 2. Check duplicate email if provided
    if email:
        existing_email = execute_query("SELECT id FROM users WHERE email = %s", (email,), fetchone=True)
        if existing_email:
            return False, {"message": "Email address is already registered.", "error_code": "AUTH_DUPLICATE_EMAIL"}, 409

    # 3. Lookup Role ID
    role = execute_query("SELECT id, name FROM roles WHERE name = %s", (role_name,), fetchone=True)
    if not role:
        return False, {"message": f"Invalid role: {role_name}", "error_code": "INVALID_ROLE"}, 400

    # 4. Status determination rule:
    # Parent Guardian -> ACTIVE
    # Volunteer, Police, Medical, Help Center -> PENDING until approved
    initial_status = 'ACTIVE' if role_name == 'PARENT_GUARDIAN' else 'PENDING'
    is_verified = 1 if role_name == 'PARENT_GUARDIAN' else 0

    user_uuid = f"usr-{role_name.lower().replace('_', '-')}-{generate_uuid()[:8]}"
    hashed_pwd = hash_password(payload.get('password'))

    query = """
    INSERT INTO users (uuid, full_name, mobile, email, password_hash, role_id, preferred_language, status, is_verified, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
    """
    try:
        user_id = execute_query(query, (
            user_uuid, full_name, mobile, email, hashed_pwd, role['id'], preferred_lang, initial_status, is_verified
        ), commit=True)

        log_audit_event(
            user_id=user_id,
            action="REGISTER",
            details={"role": role_name, "status": initial_status, "mobile": mobile},
            ip_address=ip_address,
            user_agent=user_agent
        )

        return True, {
            "user_id": user_id,
            "uuid": user_uuid,
            "full_name": full_name,
            "mobile": mobile,
            "email": email,
            "role": role_name,
            "status": initial_status,
            "requires_approval": (initial_status == 'PENDING')
        }, 201

    except Exception as e:
        return False, {"message": f"Registration failed due to a database error: {str(e)}", "error_code": "SERVER_ERROR"}, 500

def login_user(identifier, password, ip_address=None, user_agent=None):
    if not identifier or not password:
        return False, {"message": "Mobile/Email and Password are required.", "error_code": "MISSING_CREDENTIALS"}, 400

    identifier_clean = identifier.strip().lower()

    # Query by mobile or email
    query = """
    SELECT 
        u.id, u.uuid, u.full_name, u.mobile, u.email, u.password_hash, 
        u.status, u.preferred_language, u.profile_photo, u.last_login_at,
        r.id as role_id, r.name as role_name
    FROM users u
    JOIN roles r ON u.role_id = r.id
    WHERE u.mobile = %s OR LOWER(u.email) = %s
    """
    user = execute_query(query, (identifier_clean, identifier_clean), fetchone=True)

    if not user or not verify_password(user['password_hash'], password):
        log_audit_event(
            user_id=user['id'] if user else None,
            action="LOGIN_FAILED",
            details={"identifier": identifier_clean, "reason": "Invalid credentials"},
            ip_address=ip_address,
            user_agent=user_agent
        )
        return False, {"message": "Invalid credentials provided.", "error_code": "AUTH_INVALID_CREDENTIALS"}, 401

    # Status validation
    status = user['status']
    if status == 'PENDING':
        return False, {"message": "Your account is pending administrative approval. Please contact system admin.", "error_code": "AUTH_ACCOUNT_PENDING"}, 403
    elif status == 'SUSPENDED':
        return False, {"message": "Your account is currently suspended. Please contact administrator.", "error_code": "AUTH_ACCOUNT_SUSPENDED"}, 403
    elif status == 'BLOCKED':
        return False, {"message": "Your account has been blocked due to security reasons.", "error_code": "AUTH_ACCOUNT_BLOCKED"}, 403
    elif status == 'REJECTED':
        return False, {"message": "Your account registration was rejected by administrators.", "error_code": "AUTH_ACCOUNT_REJECTED"}, 403

    # Generate session token
    session_token = f"reunite_sess_{secrets.token_urlsafe(32)}"
    expires_at = datetime.now() + Config.SESSION_DURATION

    sess_query = """
    INSERT INTO user_sessions (user_id, session_token, ip_address, user_agent, created_at, expires_at)
    VALUES (%s, %s, %s, %s, NOW(), %s)
    """
    execute_query(sess_query, (user['id'], session_token, ip_address, user_agent, expires_at), commit=True)

    # Update last login
    execute_query("UPDATE users SET last_login_at = NOW() WHERE id = %s", (user['id'],), commit=True)

    # Record Audit Log
    log_audit_event(
        user_id=user['id'],
        action="LOGIN",
        details={"role": user['role_name']},
        ip_address=ip_address,
        user_agent=user_agent
    )

    # Map Role to Dashboard URL
    dashboard_map = {
        'PARENT_GUARDIAN': '/dashboard/parent.html',
        'VOLUNTEER': '/dashboard/volunteer.html',
        'POLICE_OFFICER': '/dashboard/police.html',
        'MEDICAL_STAFF': '/dashboard/medical.html',
        'HELP_CENTER_OPERATOR': '/dashboard/help-center.html',
        'EVENT_ADMIN': '/admin/dashboard.html',
        'SUPER_ADMIN': '/admin/dashboard.html'
    }

    return True, {
        "session_token": session_token,
        "expires_at": expires_at.isoformat(),
        "user": {
            "id": user['id'],
            "uuid": user['uuid'],
            "full_name": user['full_name'],
            "mobile": user['mobile'],
            "email": user['email'],
            "role": user['role_name'],
            "status": user['status'],
            "preferred_language": user['preferred_language'],
            "profile_photo": user['profile_photo']
        },
        "redirect_url": dashboard_map.get(user['role_name'], '/dashboard/parent.html')
    }, 200

def logout_user(session_token, user_id, ip_address=None, user_agent=None):
    if session_token:
        execute_query("UPDATE user_sessions SET revoked_at = NOW() WHERE session_token = %s", (session_token,), commit=True)
    
    log_audit_event(
        user_id=user_id,
        action="LOGOUT",
        details={"session_token": session_token[:15] + "..."},
        ip_address=ip_address,
        user_agent=user_agent
    )
    return True, {"message": "Logged out successfully."}, 200

def forgot_password_request(identifier):
    if not identifier:
        return False, {"message": "Mobile or Email is required.", "error_code": "INVALID_INPUT"}, 400

    identifier_clean = identifier.strip().lower()
    user = execute_query("SELECT id, email, full_name FROM users WHERE mobile = %s OR LOWER(email) = %s", (identifier_clean, identifier_clean), fetchone=True)
    
    # Generic message for security (don't expose existence of email)
    if not user:
        return True, {"message": "If an account matches the provided detail, a password reset token has been generated."}, 200

    reset_token = f"rst_{secrets.token_hex(20)}"
    expires_at = datetime.now() + Config.PASSWORD_RESET_TOKEN_DURATION

    execute_query("""
    INSERT INTO password_reset_tokens (user_id, token, created_at, expires_at)
    VALUES (%s, %s, NOW(), %s)
    """, (user['id'], reset_token, expires_at), commit=True)

    log_audit_event(
        user_id=user['id'],
        action="PASSWORD_RESET_REQUESTED",
        details={"reset_token_issued": reset_token[:10] + "..."}
    )

    return True, {
        "message": "Password reset token generated successfully.",
        "reset_token": reset_token  # Returned for testing/demo purposes
    }, 200

def reset_password(token, new_password, confirm_password):
    if not token or not new_password:
        return False, {"message": "Token and new password are required.", "error_code": "INVALID_INPUT"}, 400

    if new_password != confirm_password:
        return False, {"message": "Passwords do not match.", "error_code": "PASSWORD_MISMATCH"}, 422

    # Check token validity
    reset_rec = execute_query("""
    SELECT r.*, u.id as user_id 
    FROM password_reset_tokens r
    JOIN users u ON r.user_id = u.id
    WHERE r.token = %s AND r.used_at IS NULL AND r.expires_at > NOW()
    """, (token,), fetchone=True)

    if not reset_rec:
        return False, {"message": "Invalid, expired, or already used reset token.", "error_code": "INVALID_RESET_TOKEN"}, 400

    new_hash = hash_password(new_password)
    execute_query("UPDATE users SET password_hash = %s, updated_at = NOW() WHERE id = %s", (new_hash, reset_rec['user_id']), commit=True)
    execute_query("UPDATE password_reset_tokens SET used_at = NOW() WHERE id = %s", (reset_rec['id'],), commit=True)

    log_audit_event(
        user_id=reset_rec['user_id'],
        action="PASSWORD_RESET_COMPLETED",
        details={"token_id": reset_rec['id']}
    )

    return True, {"message": "Password has been reset successfully. Please login with your new password."}, 200

def change_password(user_id, current_password, new_password, confirm_password):
    if not current_password or not new_password:
        return False, {"message": "Current and new password are required.", "error_code": "INVALID_INPUT"}, 400

    if new_password != confirm_password:
        return False, {"message": "New passwords do not match.", "error_code": "PASSWORD_MISMATCH"}, 422

    user = execute_query("SELECT password_hash FROM users WHERE id = %s", (user_id,), fetchone=True)
    if not user or not verify_password(user['password_hash'], current_password):
        return False, {"message": "Current password is incorrect.", "error_code": "AUTH_INVALID_CREDENTIALS"}, 401

    new_hash = hash_password(new_password)
    execute_query("UPDATE users SET password_hash = %s, updated_at = NOW() WHERE id = %s", (new_hash, user_id), commit=True)

    log_audit_event(
        user_id=user_id,
        action="PASSWORD_CHANGE",
        details="User manually updated their password"
    )

    return True, {"message": "Password updated successfully."}, 200

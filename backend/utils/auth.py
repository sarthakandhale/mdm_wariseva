from functools import wraps
from flask import request, jsonify
from datetime import datetime
from db import execute_query

def get_token_from_request():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == 'bearer':
            return parts[1]
    
    token = request.headers.get('X-Session-Token')
    if token:
        return token
        
    return request.cookies.get('session_token')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_request()
        if not token:
            return jsonify({
                "success": False,
                "message": "Authentication token is missing.",
                "error_code": "AUTH_TOKEN_MISSING"
            }), 401

        query = """
        SELECT 
            s.session_token, s.expires_at, s.revoked_at,
            u.id as user_id, u.uuid, u.full_name, u.mobile, u.email, 
            u.status, u.preferred_language, u.profile_photo, u.last_login_at,
            r.id as role_id, r.name as role_name
        FROM user_sessions s
        JOIN users u ON s.user_id = u.id
        JOIN roles r ON u.role_id = r.id
        WHERE s.session_token = %s
        """
        session = execute_query(query, (token,), fetchone=True)
        
        if not session:
            return jsonify({
                "success": False,
                "message": "Invalid or expired session token.",
                "error_code": "AUTH_INVALID_TOKEN"
            }), 401

        if session['revoked_at'] is not None:
            return jsonify({
                "success": False,
                "message": "Session has been logged out/revoked.",
                "error_code": "AUTH_SESSION_REVOKED"
            }), 401

        # Check expiration
        expires_at = session['expires_at']
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at.replace('Z', ''))
        
        if expires_at < datetime.now():
            return jsonify({
                "success": False,
                "message": "Session has expired. Please log in again.",
                "error_code": "AUTH_SESSION_EXPIRED"
            }), 401

        # Check user status
        user_status = session['status']
        if user_status == 'PENDING':
            return jsonify({
                "success": False,
                "message": "Your account is pending administrative approval.",
                "error_code": "AUTH_ACCOUNT_PENDING"
            }), 403
        elif user_status == 'SUSPENDED':
            return jsonify({
                "success": False,
                "message": "Your account has been temporarily suspended.",
                "error_code": "AUTH_ACCOUNT_SUSPENDED"
            }), 403
        elif user_status == 'BLOCKED':
            return jsonify({
                "success": False,
                "message": "Your account has been blocked.",
                "error_code": "AUTH_ACCOUNT_BLOCKED"
            }), 403
        elif user_status == 'REJECTED':
            return jsonify({
                "success": False,
                "message": "Your registration request was rejected by administrators.",
                "error_code": "AUTH_ACCOUNT_REJECTED"
            }), 403

        # Attach user to request
        request.current_user = session
        return f(*args, **kwargs)

    return decorated

def permission_required(permission_name):
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(*args, **kwargs):
            user = getattr(request, 'current_user', None)
            if not user:
                return jsonify({"success": False, "message": "Unauthorized", "error_code": "UNAUTHORIZED"}), 401
                
            # Super admin bypass
            if user['role_name'] == 'SUPER_ADMIN':
                return f(*args, **kwargs)

            # Check role permissions in database
            query = """
            SELECT COUNT(*) as perm_count
            FROM role_permissions rp
            JOIN permissions p ON rp.permission_id = p.id
            WHERE rp.role_id = %s AND p.name = %s
            """
            res = execute_query(query, (user['role_id'], permission_name), fetchone=True)
            if not res or res['perm_count'] == 0:
                return jsonify({
                    "success": False,
                    "message": f"Forbidden: You lack the '{permission_name}' permission.",
                    "error_code": "FORBIDDEN_INSUFFICIENT_PERMISSIONS"
                }), 403

            return f(*args, **kwargs)
        return decorated
    return decorator

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(*args, **kwargs):
            user = getattr(request, 'current_user', None)
            if not user:
                return jsonify({"success": False, "message": "Unauthorized", "error_code": "UNAUTHORIZED"}), 401
                
            if user['role_name'] not in allowed_roles and user['role_name'] != 'SUPER_ADMIN':
                return jsonify({
                    "success": False,
                    "message": "Forbidden: Your role does not have access to this resource.",
                    "error_code": "FORBIDDEN_ROLE"
                }), 403
                
            return f(*args, **kwargs)
        return decorated
    return decorator

from db import execute_query
from utils.validators import validate_full_name, validate_email, validate_mobile
from services.audit_service import log_audit_event

def get_user_by_id(user_id):
    query = """
    SELECT 
        u.id, u.uuid, u.full_name, u.mobile, u.email, u.profile_photo, 
        u.preferred_language, u.status, u.is_verified, u.created_at, 
        u.updated_at, u.last_login_at,
        r.id as role_id, r.name as role_name, r.description as role_description
    FROM users u
    JOIN roles r ON u.role_id = r.id
    WHERE u.id = %s
    """
    user = execute_query(query, (user_id,), fetchone=True)
    if not user:
        return None
    return user

def update_user_profile(user_id, data, current_user_id=None):
    user = get_user_by_id(user_id)
    if not user:
        return False, {"message": "User not found.", "error_code": "USER_NOT_FOUND"}, 404

    updates = []
    params = []

    # Full Name
    if 'full_name' in data and data['full_name']:
        valid_name, name_err = validate_full_name(data['full_name'])
        if not valid_name:
            return False, {"message": name_err, "error_code": "VALIDATION_ERROR"}, 422
        updates.append("full_name = %s")
        params.append(data['full_name'].strip())

    # Email
    if 'email' in data:
        new_email = data['email'].strip().lower() if data['email'] else None
        if new_email and new_email != user['email']:
            valid_e, e_err = validate_email(new_email)
            if not valid_e:
                return False, {"message": e_err, "error_code": "VALIDATION_ERROR"}, 422
            existing = execute_query("SELECT id FROM users WHERE email = %s AND id != %s", (new_email, user_id), fetchone=True)
            if existing:
                return False, {"message": "Email is already taken by another user.", "error_code": "DUPLICATE_EMAIL"}, 409
            updates.append("email = %s")
            params.append(new_email)
        elif new_email is None and user['email'] is not None:
            updates.append("email = NULL")

    # Preferred Language
    if 'preferred_language' in data:
        updates.append("preferred_language = %s")
        params.append(data['preferred_language'])

    # Profile Photo
    if 'profile_photo' in data:
        updates.append("profile_photo = %s")
        params.append(data['profile_photo'])

    # Mobile logic: require verification token if changing mobile
    if 'mobile' in data and data['mobile']:
        valid_mob, mob_res = validate_mobile(data['mobile'])
        if not valid_mob:
            return False, {"message": mob_res, "error_code": "VALIDATION_ERROR"}, 422
        if mob_res != user['mobile']:
            verification_code = data.get('mobile_verification_code')
            if verification_code != '123456': # Standard demo OTP code verification
                return False, {"message": "Mobile number change requires OTP verification. Please verify SMS OTP code.", "error_code": "OTP_VERIFICATION_REQUIRED"}, 400
            
            existing_m = execute_query("SELECT id FROM users WHERE mobile = %s AND id != %s", (mob_res, user_id), fetchone=True)
            if existing_m:
                return False, {"message": "Mobile number is already registered to another account.", "error_code": "DUPLICATE_MOBILE"}, 409
            updates.append("mobile = %s")
            params.append(mob_res)

    if not updates:
        return True, {"message": "No changes made.", "user": user}, 200

    updates.append("updated_at = NOW()")
    sql = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
    params.append(user_id)

    execute_query(sql, tuple(params), commit=True)

    log_audit_event(
        user_id=current_user_id or user_id,
        action="PROFILE_UPDATE",
        details={"updated_fields": list(data.keys()), "target_user_id": user_id}
    )

    updated_user = get_user_by_id(user_id)
    return True, {"message": "Profile updated successfully.", "user": updated_user}, 200

def list_users(status=None, role=None, search=None, limit=50, offset=0):
    where_clauses = []
    params = []

    if status:
        where_clauses.append("u.status = %s")
        params.append(status)

    if role:
        where_clauses.append("r.name = %s")
        params.append(role)

    if search:
        where_clauses.append("(u.full_name LIKE %s OR u.mobile LIKE %s OR u.email LIKE %s)")
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern, search_pattern])

    where_str = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    query = f"""
    SELECT 
        u.id, u.uuid, u.full_name, u.mobile, u.email, u.profile_photo, 
        u.preferred_language, u.status, u.is_verified, u.created_at, u.last_login_at,
        r.name as role_name, r.description as role_description
    FROM users u
    JOIN roles r ON u.role_id = r.id
    {where_str}
    ORDER BY u.created_at DESC
    LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])
    users = execute_query(query, tuple(params), fetchall=True)

    # Count total
    count_query = f"SELECT COUNT(*) as total FROM users u JOIN roles r ON u.role_id = r.id {where_str}"
    count_params = params[:-2]
    count_res = execute_query(count_query, tuple(count_params), fetchone=True)

    return {
        "users": users,
        "total": count_res['total'] if count_res else 0,
        "limit": limit,
        "offset": offset
    }

def update_user_status(target_user_id, action_type, admin_user):
    target = get_user_by_id(target_user_id)
    if not target:
        return False, {"message": "Target user not found.", "error_code": "USER_NOT_FOUND"}, 404

    # Prevent target user from being SUPER_ADMIN unless actor is SUPER_ADMIN
    if target['role_name'] == 'SUPER_ADMIN' and admin_user['role_name'] != 'SUPER_ADMIN':
        return False, {"message": "Cannot modify SUPER_ADMIN status.", "error_code": "FORBIDDEN"}, 403

    status_map = {
        'approve': 'ACTIVE',
        'reject': 'REJECTED',
        'suspend': 'SUSPENDED',
        'block': 'BLOCKED',
        'activate': 'ACTIVE'
    }

    new_status = status_map.get(action_type.lower())
    if not new_status:
        return False, {"message": f"Invalid status action: {action_type}", "error_code": "INVALID_ACTION"}, 400

    execute_query("UPDATE users SET status = %s, updated_at = NOW() WHERE id = %s", (new_status, target_user_id), commit=True)

    action_audit_name = f"USER_{action_type.upper()}"
    log_audit_event(
        user_id=admin_user['user_id'],
        action=action_audit_name,
        details={
            "target_user_id": target_user_id,
            "target_mobile": target['mobile'],
            "previous_status": target['status'],
            "new_status": new_status
        }
    )

    return True, {
        "message": f"User status successfully updated to {new_status}.",
        "user_id": target_user_id,
        "new_status": new_status
    }, 200

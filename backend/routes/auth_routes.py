from flask import Blueprint, request, jsonify
from services.auth_service import register_user, login_user, logout_user, forgot_password_request, reset_password, change_password
from utils.auth import token_required, get_token_from_request

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def handle_register():
    data = request.get_json() or {}
    success, result, status_code = register_user(
        data, 
        ip_address=request.remote_addr, 
        user_agent=request.headers.get('User-Agent')
    )
    if success:
        return jsonify({"success": True, "message": "Registration successful.", "data": result}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code'), "errors": result.get('errors')}), status_code

@auth_bp.route('/login', methods=['POST'])
def handle_login():
    data = request.get_json() or {}
    identifier = data.get('identifier') or data.get('mobile') or data.get('email')
    password = data.get('password')
    
    success, result, status_code = login_user(
        identifier, password, 
        ip_address=request.remote_addr, 
        user_agent=request.headers.get('User-Agent')
    )
    if success:
        return jsonify({"success": True, "message": "Login successful.", "data": result}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code')}), status_code

@auth_bp.route('/logout', methods=['POST'])
@token_required
def handle_logout():
    token = get_token_from_request()
    current_user = getattr(request, 'current_user', {})
    success, result, status_code = logout_user(
        token, 
        current_user.get('user_id'),
        ip_address=request.remote_addr, 
        user_agent=request.headers.get('User-Agent')
    )
    return jsonify({"success": True, "message": result.get('message'), "data": {}}), status_code

@auth_bp.route('/forgot-password', methods=['POST'])
def handle_forgot_password():
    data = request.get_json() or {}
    identifier = data.get('identifier') or data.get('email') or data.get('mobile')
    success, result, status_code = forgot_password_request(identifier)
    if success:
        return jsonify({"success": True, "message": result.get('message'), "data": result}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code')}), status_code

@auth_bp.route('/reset-password', methods=['POST'])
def handle_reset_password():
    data = request.get_json() or {}
    token = data.get('token')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    
    success, result, status_code = reset_password(token, new_password, confirm_password)
    if success:
        return jsonify({"success": True, "message": result.get('message'), "data": {}}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code')}), status_code

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def handle_change_password():
    data = request.get_json() or {}
    current_user = getattr(request, 'current_user', {})
    user_id = current_user.get('user_id')
    current_pwd = data.get('current_password')
    new_pwd = data.get('new_password')
    confirm_pwd = data.get('confirm_password')
    
    success, result, status_code = change_password(user_id, current_pwd, new_pwd, confirm_pwd)
    if success:
        return jsonify({"success": True, "message": result.get('message'), "data": {}}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code')}), status_code

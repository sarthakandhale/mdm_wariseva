from flask import Blueprint, request, jsonify
from services.user_service import get_user_by_id, update_user_profile
from utils.auth import token_required
from db import execute_query

user_bp = Blueprint('user', __name__, url_prefix='/api/users')

@user_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    current_user = getattr(request, 'current_user', {})
    user_id = current_user.get('user_id')
    user_data = get_user_by_id(user_id)
    if not user_data:
        return jsonify({"success": False, "message": "User profile not found.", "error_code": "NOT_FOUND"}), 404
        
    return jsonify({"success": True, "message": "User profile retrieved.", "data": user_data}), 200

@user_bp.route('/me', methods=['PUT'])
@token_required
def update_current_user():
    current_user = getattr(request, 'current_user', {})
    user_id = current_user.get('user_id')
    data = request.get_json() or {}
    
    success, result, status_code = update_user_profile(user_id, data, current_user_id=user_id)
    if success:
        return jsonify({"success": True, "message": result.get('message'), "data": result.get('user')}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code')}), status_code

@user_bp.route('/<int:user_id>', methods=['GET'])
@token_required
def get_user_by_id_route(user_id):
    user_data = get_user_by_id(user_id)
    if not user_data:
        return jsonify({"success": False, "message": "User not found.", "error_code": "NOT_FOUND"}), 404
        
    return jsonify({"success": True, "message": "User details retrieved.", "data": user_data}), 200

# Roles and Permissions endpoint
@user_bp.route('/roles', methods=['GET'])
def get_roles():
    roles = execute_query("SELECT id, name, description FROM roles ORDER BY id ASC", fetchall=True)
    return jsonify({"success": True, "message": "Roles list retrieved.", "data": roles}), 200

@user_bp.route('/roles/<int:role_id>/permissions', methods=['GET'])
@token_required
def get_role_permissions(role_id):
    query = """
    SELECT p.id, p.name, p.description 
    FROM permissions p
    JOIN role_permissions rp ON p.id = rp.permission_id
    WHERE rp.role_id = %s
    """
    permissions = execute_query(query, (role_id,), fetchall=True)
    return jsonify({"success": True, "message": "Role permissions retrieved.", "data": permissions}), 200

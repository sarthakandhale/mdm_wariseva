from flask import Blueprint, request, jsonify
from services.user_service import list_users, update_user_status, get_user_by_id
from utils.auth import token_required, role_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/users', methods=['GET'])
@token_required
@role_required(['EVENT_ADMIN', 'SUPER_ADMIN'])
def get_all_users():
    status = request.args.get('status')
    role = request.args.get('role')
    search = request.args.get('search')
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    
    result = list_users(status=status, role=role, search=search, limit=limit, offset=offset)
    return jsonify({"success": True, "message": "Users list retrieved.", "data": result}), 200

@admin_bp.route('/users/pending', methods=['GET'])
@token_required
@role_required(['EVENT_ADMIN', 'SUPER_ADMIN'])
def get_pending_users():
    search = request.args.get('search')
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    
    result = list_users(status='PENDING', search=search, limit=limit, offset=offset)
    return jsonify({"success": True, "message": "Pending users list retrieved.", "data": result}), 200

@admin_bp.route('/users/<int:user_id>/approve', methods=['PUT'])
@token_required
@role_required(['EVENT_ADMIN', 'SUPER_ADMIN'])
def approve_user(user_id):
    admin_user = getattr(request, 'current_user', {})
    success, result, status_code = update_user_status(user_id, 'approve', admin_user)
    if success:
        return jsonify({"success": True, "message": result.get('message'), "data": result}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code')}), status_code

@admin_bp.route('/users/<int:user_id>/reject', methods=['PUT'])
@token_required
@role_required(['EVENT_ADMIN', 'SUPER_ADMIN'])
def reject_user(user_id):
    admin_user = getattr(request, 'current_user', {})
    success, result, status_code = update_user_status(user_id, 'reject', admin_user)
    if success:
        return jsonify({"success": True, "message": result.get('message'), "data": result}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code')}), status_code

@admin_bp.route('/users/<int:user_id>/suspend', methods=['PUT'])
@token_required
@role_required(['EVENT_ADMIN', 'SUPER_ADMIN'])
def suspend_user(user_id):
    admin_user = getattr(request, 'current_user', {})
    success, result, status_code = update_user_status(user_id, 'suspend', admin_user)
    if success:
        return jsonify({"success": True, "message": result.get('message'), "data": result}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code')}), status_code

@admin_bp.route('/users/<int:user_id>/block', methods=['PUT'])
@token_required
@role_required(['EVENT_ADMIN', 'SUPER_ADMIN'])
def block_user(user_id):
    admin_user = getattr(request, 'current_user', {})
    success, result, status_code = update_user_status(user_id, 'block', admin_user)
    if success:
        return jsonify({"success": True, "message": result.get('message'), "data": result}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code')}), status_code

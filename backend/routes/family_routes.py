from flask import Blueprint, request, jsonify
from utils.auth import token_required
from utils.authorization import verify_family_access, verify_person_access
from services.family_service import create_family, get_family_by_id, list_families_for_user, update_family, delete_family
from services.person_service import create_person_profile, get_person_full_profile, update_person_profile, deactivate_person

family_bp = Blueprint('family', __name__, url_prefix='/api/families')

@family_bp.route('', methods=['POST'])
@token_required
def handle_create_family():
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}
    success, result, status_code = create_family(payload, current_user)
    if success:
        return jsonify({"success": True, "message": "Family created successfully.", "data": result}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code')}), status_code

@family_bp.route('', methods=['GET'])
@token_required
def handle_list_families():
    current_user = getattr(request, 'current_user', {})
    families = list_families_for_user(current_user)
    return jsonify({"success": True, "message": "Families list retrieved.", "data": families}), 200

@family_bp.route('/<int:family_id>', methods=['GET'])
@token_required
def handle_get_family(family_id):
    current_user = getattr(request, 'current_user', {})
    allowed, family = verify_family_access(family_id, current_user, required_level='VIEWER')
    if not allowed:
        return jsonify({"success": False, "message": "Forbidden: You are not authorized to view this family.", "error_code": "FORBIDDEN_FAMILY_ACCESS"}), 403

    full_detail = get_family_by_id(family_id, current_user)
    return jsonify({"success": True, "message": "Family details retrieved.", "data": full_detail}), 200

@family_bp.route('/<int:family_id>', methods=['PUT'])
@token_required
def handle_update_family(family_id):
    current_user = getattr(request, 'current_user', {})
    allowed, family = verify_family_access(family_id, current_user, required_level='EDITOR')
    if not allowed:
        return jsonify({"success": False, "message": "Forbidden: You are not authorized to edit this family.", "error_code": "FORBIDDEN_FAMILY_ACCESS"}), 403

    payload = request.get_json() or {}
    success, result, status_code = update_family(family_id, payload, current_user)
    if success:
        return jsonify({"success": True, "message": "Family updated successfully.", "data": result}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code')}), status_code

@family_bp.route('/<int:family_id>', methods=['DELETE'])
@token_required
def handle_delete_family(family_id):
    current_user = getattr(request, 'current_user', {})
    allowed, family = verify_family_access(family_id, current_user, required_level='OWNER')
    if not allowed:
        return jsonify({"success": False, "message": "Forbidden: Only the family owner can delete this family.", "error_code": "FORBIDDEN_FAMILY_ACCESS"}), 403

    success, result, status_code = delete_family(family_id, current_user)
    if success:
        return jsonify({"success": True, "message": result.get('message'), "data": {}}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code')}), status_code

# Member Management Routes
@family_bp.route('/<int:family_id>/members', methods=['POST'])
@token_required
def handle_add_family_member(family_id):
    current_user = getattr(request, 'current_user', {})
    allowed, family = verify_family_access(family_id, current_user, required_level='EDITOR')
    if not allowed:
        return jsonify({"success": False, "message": "Forbidden: You are not authorized to add members to this family.", "error_code": "FORBIDDEN_FAMILY_ACCESS"}), 403

    payload = request.get_json() or {}
    success, result, status_code = create_person_profile(family_id, payload, current_user)
    if success:
        return jsonify({"success": True, "message": "Family member added successfully.", "data": result}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code')}), status_code

@family_bp.route('/<int:family_id>/members', methods=['GET'])
@token_required
def handle_list_family_members(family_id):
    current_user = getattr(request, 'current_user', {})
    allowed, family = verify_family_access(family_id, current_user, required_level='VIEWER')
    if not allowed:
        return jsonify({"success": False, "message": "Forbidden: You are not authorized to view members of this family.", "error_code": "FORBIDDEN_FAMILY_ACCESS"}), 403

    full_detail = get_family_by_id(family_id, current_user)
    return jsonify({"success": True, "message": "Family members list retrieved.", "data": full_detail.get('members', [])}), 200

@family_bp.route('/<int:family_id>/members/<int:person_id>', methods=['GET'])
@token_required
def handle_get_family_member(family_id, person_id):
    current_user = getattr(request, 'current_user', {})
    allowed, family = verify_family_access(family_id, current_user, required_level='VIEWER')
    if not allowed:
        return jsonify({"success": False, "message": "Forbidden: Access denied to family member.", "error_code": "FORBIDDEN_FAMILY_ACCESS"}), 403

    person = get_person_full_profile(person_id, current_user)
    if not person:
        return jsonify({"success": False, "message": "Person profile not found.", "error_code": "NOT_FOUND"}), 404
    return jsonify({"success": True, "message": "Member details retrieved.", "data": person}), 200

@family_bp.route('/<int:family_id>/members/<int:person_id>', methods=['PUT'])
@token_required
def handle_update_family_member(family_id, person_id):
    current_user = getattr(request, 'current_user', {})
    allowed, family = verify_family_access(family_id, current_user, required_level='EDITOR')
    if not allowed:
        return jsonify({"success": False, "message": "Forbidden: Cannot edit member in this family.", "error_code": "FORBIDDEN_FAMILY_ACCESS"}), 403

    payload = request.get_json() or {}
    success, result, status_code = update_person_profile(person_id, payload, current_user)
    if success:
        return jsonify({"success": True, "message": "Family member profile updated.", "data": result}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code')}), status_code

@family_bp.route('/<int:family_id>/members/<int:person_id>/deactivate', methods=['PATCH'])
@token_required
def handle_deactivate_family_member(family_id, person_id):
    current_user = getattr(request, 'current_user', {})
    allowed, family = verify_family_access(family_id, current_user, required_level='EDITOR')
    if not allowed:
        return jsonify({"success": False, "message": "Forbidden: Cannot deactivate member in this family.", "error_code": "FORBIDDEN_FAMILY_ACCESS"}), 403

    success, result, status_code = deactivate_person(person_id, current_user)
    if success:
        return jsonify({"success": True, "message": result.get('message'), "data": {}}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code')}), status_code

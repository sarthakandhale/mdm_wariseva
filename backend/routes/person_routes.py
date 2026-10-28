from flask import Blueprint, request, jsonify
from utils.auth import token_required
from utils.authorization import verify_person_access
from services.person_service import get_person_full_profile, update_person_profile

person_bp = Blueprint('person', __name__, url_prefix='/api/persons')

@person_bp.route('/<int:person_id>', methods=['GET'])
@token_required
def get_person(person_id):
    current_user = getattr(request, 'current_user', {})
    allowed, person, family = verify_person_access(person_id, current_user, required_level='VIEWER')
    if not allowed:
        return jsonify({"success": False, "message": "Forbidden: You are not authorized to view this person profile.", "error_code": "FORBIDDEN_PERSON_ACCESS"}), 403

    full_profile = get_person_full_profile(person_id, current_user)
    if not full_profile:
        return jsonify({"success": False, "message": "Person profile not found.", "error_code": "NOT_FOUND"}), 404

    return jsonify({"success": True, "message": "Person profile retrieved.", "data": full_profile}), 200

@person_bp.route('/<int:person_id>', methods=['PUT'])
@token_required
def update_person(person_id):
    current_user = getattr(request, 'current_user', {})
    allowed, person, family = verify_person_access(person_id, current_user, required_level='EDITOR')
    if not allowed:
        return jsonify({"success": False, "message": "Forbidden: You are not authorized to update this person profile.", "error_code": "FORBIDDEN_PERSON_ACCESS"}), 403

    payload = request.get_json() or {}
    success, result, status_code = update_person_profile(person_id, payload, current_user)
    if success:
        return jsonify({"success": True, "message": "Person profile updated.", "data": result}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code')}), status_code

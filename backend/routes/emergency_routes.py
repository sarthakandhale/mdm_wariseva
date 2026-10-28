from flask import Blueprint, request, jsonify
from utils.auth import token_required
from utils.authorization import verify_person_access
from services.emergency_service import add_emergency_contact, update_emergency_contact, delete_emergency_contact

emergency_bp = Blueprint('emergency', __name__, url_prefix='/api/persons')

@emergency_bp.route('/<int:person_id>/emergency-contacts', methods=['POST'])
@token_required
def create_emergency_contact(person_id):
    current_user = getattr(request, 'current_user', {})
    allowed, person, family = verify_person_access(person_id, current_user, required_level='EDITOR')
    if not allowed:
        return jsonify({"success": False, "message": "Forbidden: You are not authorized to modify emergency contacts for this person.", "error_code": "FORBIDDEN"}), 403

    payload = request.get_json() or {}
    success, result, status_code = add_emergency_contact(person_id, payload, current_user)
    if success:
        return jsonify({"success": True, "message": "Emergency contact added successfully.", "data": result}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code')}), status_code

@emergency_bp.route('/<int:person_id>/emergency-contacts/<int:contact_id>', methods=['PUT'])
@token_required
def update_contact(person_id, contact_id):
    current_user = getattr(request, 'current_user', {})
    allowed, person, family = verify_person_access(person_id, current_user, required_level='EDITOR')
    if not allowed:
        return jsonify({"success": False, "message": "Forbidden: Cannot edit emergency contact.", "error_code": "FORBIDDEN"}), 403

    payload = request.get_json() or {}
    success, result, status_code = update_emergency_contact(person_id, contact_id, payload, current_user)
    if success:
        return jsonify({"success": True, "message": result.get('message'), "data": {}}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code')}), status_code

@emergency_bp.route('/<int:person_id>/emergency-contacts/<int:contact_id>', methods=['DELETE'])
@token_required
def delete_contact(person_id, contact_id):
    current_user = getattr(request, 'current_user', {})
    allowed, person, family = verify_person_access(person_id, current_user, required_level='EDITOR')
    if not allowed:
        return jsonify({"success": False, "message": "Forbidden: Cannot delete emergency contact.", "error_code": "FORBIDDEN"}), 403

    success, result, status_code = delete_emergency_contact(person_id, contact_id, current_user)
    if success:
        return jsonify({"success": True, "message": result.get('message'), "data": {}}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code')}), status_code

from flask import Blueprint, request, jsonify
from utils.auth import token_required, role_required
from services.found_person_service import (
    create_found_person_case, get_found_person_case_details, list_found_person_cases,
    search_existing_profiles, add_identification_clue, assign_safe_location,
    log_family_contact, perform_identity_verification, perform_reunification
)
from db import execute_query
from services.audit_service import log_audit_event

found_person_bp = Blueprint('found_person', __name__, url_prefix='/api/found-person')

@found_person_bp.route('/cases', methods=['POST'])
@token_required
@role_required(['VOLUNTEER', 'POLICE_OFFICER', 'HELP_CENTER_OPERATOR', 'MEDICAL_STAFF', 'EVENT_ADMIN', 'SUPER_ADMIN'])
def report_found_case():
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}

    success, result, status_code = create_found_person_case(payload, current_user)
    return jsonify({"success": success, "message": "Found person report created.", "data": result}), status_code

@found_person_bp.route('/cases', methods=['GET'])
@token_required
def get_found_cases():
    status = request.args.get('status')
    ident_status = request.args.get('identification_status')
    zone = request.args.get('zone')

    cases = list_found_person_cases(status=status, identification_status=ident_status, zone=zone)
    return jsonify({"success": True, "message": "Found person cases retrieved.", "data": cases}), 200

@found_person_bp.route('/cases/<int:case_id>', methods=['GET'])
@token_required
def get_found_case_by_id(case_id):
    current_user = getattr(request, 'current_user', {})
    case = get_found_person_case_details(case_id, current_user)
    if not case:
        return jsonify({"success": False, "message": "Found person case not found.", "error_code": "NOT_FOUND"}), 404
    return jsonify({"success": True, "message": "Found person case details retrieved.", "data": case}), 200

@found_person_bp.route('/cases/<int:case_id>/status', methods=['PATCH'])
@token_required
def update_found_case_status(case_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}
    new_status = payload.get('status')
    reason = payload.get('reason')

    case = execute_query("SELECT status FROM found_person_cases WHERE id = %s", (case_id,), fetchone=True)
    if not case:
        return jsonify({"success": False, "message": "Case not found.", "error_code": "NOT_FOUND"}), 404

    old_status = case['status']
    valid_statuses = ['REPORTED', 'UNDER_REVIEW', 'IDENTITY_SEARCH', 'POSSIBLE_MATCH', 'VERIFICATION', 'IDENTITY_CONFIRMED', 'FAMILY_CONTACTED', 'REUNIFICATION_PENDING', 'REUNITED', 'TRANSFERRED', 'UNRESOLVED', 'CLOSED']

    if new_status not in valid_statuses:
        return jsonify({"success": False, "message": f"Invalid status: {new_status}", "error_code": "INVALID_STATUS"}), 400

    execute_query("UPDATE found_person_cases SET status = %s, updated_at = NOW() WHERE id = %s", (new_status, case_id), commit=True)
    execute_query("INSERT INTO found_person_status_history (case_id, old_status, new_status, changed_by, reason) VALUES (%s, %s, %s, %s, %s)",
                  (case_id, old_status, new_status, current_user['user_id'], reason), commit=True)

    log_audit_event(current_user['user_id'], "FOUND_CASE_STATUS_CHANGED", {"case_id": case_id, "old": old_status, "new": new_status})

    return jsonify({"success": True, "message": f"Case status updated to {new_status}.", "data": {"new_status": new_status}}), 200

@found_person_bp.route('/cases/search-profiles', methods=['GET'])
@token_required
def search_profiles_route():
    current_user = getattr(request, 'current_user', {})
    query_str = request.args.get('q', '')
    profiles = search_existing_profiles(query_str, current_user)
    return jsonify({"success": True, "message": "Candidate profiles retrieved.", "data": profiles}), 200

@found_person_bp.route('/cases/<int:case_id>/identification-clues', methods=['POST'])
@token_required
def add_clue_route(case_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}

    success, result, status_code = add_identification_clue(case_id, payload, current_user)
    return jsonify({"success": True, "message": result.get('message'), "data": result}), status_code

@found_person_bp.route('/cases/<int:case_id>/safe-location', methods=['POST'])
@token_required
def assign_safe_location_route(case_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}

    success, result, status_code = assign_safe_location(case_id, payload, current_user)
    return jsonify({"success": True, "message": result.get('message'), "data": result}), status_code

@found_person_bp.route('/cases/<int:case_id>/family-contact', methods=['POST'])
@token_required
def log_family_contact_route(case_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}

    success, result, status_code = log_family_contact(case_id, payload, current_user)
    return jsonify({"success": True, "message": result.get('message'), "data": result}), status_code

@found_person_bp.route('/cases/<int:case_id>/verification', methods=['POST'])
@token_required
@role_required(['POLICE_OFFICER', 'HELP_CENTER_OPERATOR', 'EVENT_ADMIN', 'SUPER_ADMIN'])
def verify_identity_route(case_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}

    success, result, status_code = perform_identity_verification(case_id, payload, current_user)
    return jsonify({"success": True, "message": result.get('message'), "data": result}), status_code

@found_person_bp.route('/cases/<int:case_id>/reunification', methods=['POST'])
@token_required
@role_required(['POLICE_OFFICER', 'HELP_CENTER_OPERATOR', 'EVENT_ADMIN', 'SUPER_ADMIN'])
def perform_reunification_route(case_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}

    success, result, status_code = perform_reunification(case_id, payload, current_user)
    return jsonify({"success": True, "message": result.get('message'), "data": result}), status_code

@found_person_bp.route('/cases/<int:case_id>/notes', methods=['POST'])
@token_required
def add_found_note_route(case_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}
    note_text = payload.get('note', '').strip()
    visibility = payload.get('visibility', 'FAMILY_VISIBLE')

    note_id = execute_query("INSERT INTO found_person_notes (case_id, created_by, note, visibility) VALUES (%s, %s, %s, %s)",
                            (case_id, current_user['user_id'], note_text, visibility), commit=True)
    return jsonify({"success": True, "message": "Case note added.", "data": {"note_id": note_id}}), 201

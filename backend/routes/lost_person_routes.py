from flask import Blueprint, request, jsonify
from utils.auth import token_required, role_required
from services.lost_person_service import (
    create_lost_person_case, get_lost_person_case_details, list_lost_person_cases,
    override_case_priority, withdraw_lost_person_case, add_case_note, report_sighting,
    check_active_lost_case_for_person
)
from db import execute_query
from services.audit_service import log_audit_event

lost_person_bp = Blueprint('lost_person', __name__, url_prefix='/api/lost-person')

@lost_person_bp.route('/cases', methods=['POST'])
@token_required
def report_lost_case():
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}

    success, result, status_code = create_lost_person_case(payload, current_user)
    if success:
        return jsonify({"success": True, "message": "Missing person case reported successfully.", "data": result}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code'), "data": result.get('active_case')}), status_code

@lost_person_bp.route('/cases', methods=['GET'])
@token_required
def get_lost_cases():
    current_user = getattr(request, 'current_user', {})
    status = request.args.get('status')
    priority = request.args.get('priority')
    zone = request.args.get('zone')
    family_id = request.args.get('family_id')
    my_cases_only = request.args.get('my_cases')

    user_id_filter = current_user['user_id'] if my_cases_only else None
    cases = list_lost_person_cases(status=status, priority=priority, zone=zone, family_id=family_id, user_id=user_id_filter)
    return jsonify({"success": True, "message": "Lost person cases retrieved.", "data": cases}), 200

@lost_person_bp.route('/cases/<int:case_id>', methods=['GET'])
@token_required
def get_lost_case_by_id(case_id):
    current_user = getattr(request, 'current_user', {})
    case = get_lost_person_case_details(case_id, current_user)
    if not case:
        return jsonify({"success": False, "message": "Lost person case not found.", "error_code": "NOT_FOUND"}), 404
    return jsonify({"success": True, "message": "Lost person case details retrieved.", "data": case}), 200

@lost_person_bp.route('/cases/<int:case_id>/status', methods=['PATCH'])
@token_required
def update_case_status_route(case_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}
    new_status = payload.get('status')
    reason = payload.get('reason')

    case = execute_query("SELECT status FROM lost_person_cases WHERE id = %s", (case_id,), fetchone=True)
    if not case:
        return jsonify({"success": False, "message": "Case not found.", "error_code": "NOT_FOUND"}), 404

    old_status = case['status']
    valid_statuses = ['DRAFT', 'REPORTED', 'UNDER_REVIEW', 'SEARCHING', 'POSSIBLE_SIGHTING', 'POSSIBLE_MATCH', 'VERIFICATION', 'FOUND', 'REUNITED', 'WITHDRAWN', 'CLOSED']

    if new_status not in valid_statuses:
        return jsonify({"success": False, "message": f"Invalid status: {new_status}", "error_code": "INVALID_STATUS"}), 400

    execute_query("UPDATE lost_person_cases SET status = %s, updated_at = NOW() WHERE id = %s", (new_status, case_id), commit=True)
    execute_query("INSERT INTO lost_person_status_history (case_id, old_status, new_status, changed_by, reason) VALUES (%s, %s, %s, %s, %s)",
                  (case_id, old_status, new_status, current_user['user_id'], reason), commit=True)

    log_audit_event(current_user['user_id'], "LOST_CASE_STATUS_CHANGED", {"case_id": case_id, "old": old_status, "new": new_status})

    return jsonify({"success": True, "message": f"Case status updated to {new_status}.", "data": {"new_status": new_status}}), 200

@lost_person_bp.route('/cases/<int:case_id>/priority', methods=['PATCH'])
@token_required
@role_required(['POLICE_OFFICER', 'HELP_CENTER_OPERATOR', 'EVENT_ADMIN', 'SUPER_ADMIN'])
def override_priority_route(case_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}
    new_priority = payload.get('priority_level')
    reason = payload.get('reason', 'Police manual priority override')

    success, result, status_code = override_case_priority(case_id, new_priority, reason, current_user)
    if success:
        return jsonify({"success": True, "message": result.get('message'), "data": result}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code')}), status_code

@lost_person_bp.route('/cases/<int:case_id>/withdraw', methods=['POST'])
@token_required
def withdraw_case_route(case_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}
    reason = payload.get('reason', 'Found by family')

    success, result, status_code = withdraw_lost_person_case(case_id, reason, current_user)
    if success:
        return jsonify({"success": True, "message": result.get('message')}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code')}), status_code

@lost_person_bp.route('/cases/<int:case_id>/notes', methods=['POST'])
@token_required
def create_note_route(case_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}
    note_text = payload.get('note', '').strip()
    visibility = payload.get('visibility', 'FAMILY_VISIBLE')

    if not note_text:
        return jsonify({"success": False, "message": "Note content is required.", "error_code": "EMPTY_NOTE"}), 400

    success, result, status_code = add_case_note(case_id, note_text, visibility, current_user)
    return jsonify({"success": True, "message": result.get('message'), "data": result}), status_code

@lost_person_bp.route('/cases/<int:case_id>/sightings', methods=['POST'])
@token_required
def create_sighting_route(case_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}

    success, result, status_code = report_sighting(case_id, payload, current_user)
    if success:
        return jsonify({"success": True, "message": result.get('message'), "data": result}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code')}), status_code

@lost_person_bp.route('/cases/<int:case_id>/search-request', methods=['POST'])
@token_required
def create_search_request_route(case_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}

    req_id = execute_query("""
    INSERT INTO lost_person_search_requests (case_id, requested_by, zone, priority, description, status)
    VALUES (%s, %s, %s, %s, %s, 'REQUESTED')
    """, (
        case_id, current_user['user_id'],
        payload.get('zone', 'Saswad'),
        payload.get('priority', 'HIGH'),
        payload.get('description', 'Volunteer search support requested for missing case')
    ), commit=True)

    log_audit_event(current_user['user_id'], "LOST_CASE_SEARCH_REQUESTED", {"case_id": case_id, "request_id": req_id})
    return jsonify({"success": True, "message": "Search support requested successfully.", "data": {"request_id": req_id}}), 201

# Person & Family Active Case Checks
@lost_person_bp.route('/active-case/person/<int:person_id>', methods=['GET'])
@token_required
def check_person_active_case(person_id):
    active_case = check_active_lost_case_for_person(person_id)
    return jsonify({"success": True, "has_active_case": bool(active_case), "data": active_case}), 200

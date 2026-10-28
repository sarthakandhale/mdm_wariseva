from flask import Blueprint, request, jsonify
from utils.auth import token_required, role_required
from services.item_service import (
    create_lost_item_case, create_found_item_case, get_lost_item_details,
    get_found_item_details, list_lost_items, list_found_items,
    submit_item_claim, verify_claim, manual_match_items, release_found_item
)
from db import execute_query
from services.audit_service import log_audit_event

item_bp = Blueprint('items', __name__, url_prefix='/api')

# --- LOST ITEMS ---
@item_bp.route('/lost-items', methods=['POST'])
@token_required
def report_lost_item_route():
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}

    success, result, status_code = create_lost_item_case(payload, current_user)
    return jsonify({"success": success, "message": "Lost item case reported.", "data": result}), status_code

@item_bp.route('/lost-items', methods=['GET'])
@token_required
def get_lost_items_route():
    category = request.args.get('category')
    zone = request.args.get('zone')
    status = request.args.get('status')

    cases = list_lost_items(category=category, zone=zone, status=status)
    return jsonify({"success": True, "message": "Lost item cases retrieved.", "data": cases}), 200

@item_bp.route('/lost-items/<int:case_id>', methods=['GET'])
@token_required
def get_lost_item_by_id_route(case_id):
    current_user = getattr(request, 'current_user', {})
    case = get_lost_item_details(case_id, current_user)
    if not case:
        return jsonify({"success": False, "message": "Lost item case not found.", "error_code": "NOT_FOUND"}), 404
    return jsonify({"success": True, "message": "Lost item details retrieved.", "data": case}), 200

# --- FOUND ITEMS ---
@item_bp.route('/found-items', methods=['POST'])
@token_required
@role_required(['VOLUNTEER', 'POLICE_OFFICER', 'HELP_CENTER_OPERATOR', 'DINDI_LEADER', 'EVENT_ADMIN', 'SUPER_ADMIN'])
def report_found_item_route():
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}

    success, result, status_code = create_found_item_case(payload, current_user)
    return jsonify({"success": success, "message": "Found item registered.", "data": result}), status_code

@item_bp.route('/found-items', methods=['GET'])
@token_required
def get_found_items_route():
    category = request.args.get('category')
    zone = request.args.get('zone')
    status = request.args.get('status')

    cases = list_found_items(category=category, zone=zone, status=status)
    return jsonify({"success": True, "message": "Found item catalog retrieved.", "data": cases}), 200

@item_bp.route('/found-items/<int:case_id>', methods=['GET'])
@token_required
def get_found_item_by_id_route(case_id):
    current_user = getattr(request, 'current_user', {})
    case = get_found_item_details(case_id, current_user)
    if not case:
        return jsonify({"success": False, "message": "Found item case not found.", "error_code": "NOT_FOUND"}), 404
    return jsonify({"success": True, "message": "Found item details retrieved.", "data": case}), 200

# --- CLAIMS ---
@item_bp.route('/found-items/<int:case_id>/claims', methods=['POST'])
@token_required
def submit_claim_route(case_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}

    success, result, status_code = submit_item_claim(case_id, payload, current_user)
    return jsonify({"success": success, "message": result.get('message'), "data": result}), status_code

@item_bp.route('/claims/<int:claim_id>/verify', methods=['POST'])
@token_required
@role_required(['POLICE_OFFICER', 'HELP_CENTER_OPERATOR', 'EVENT_ADMIN', 'SUPER_ADMIN'])
def verify_claim_route(claim_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}

    success, result, status_code = verify_claim(claim_id, payload, current_user)
    return jsonify({"success": success, "message": result.get('message')}), status_code

# --- MANUAL MATCH ---
@item_bp.route('/item-matches/manual', methods=['POST'])
@token_required
@role_required(['POLICE_OFFICER', 'HELP_CENTER_OPERATOR', 'EVENT_ADMIN', 'SUPER_ADMIN'])
def manual_match_route():
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}
    lost_id = payload.get('lost_item_case_id')
    found_id = payload.get('found_item_case_id')
    reason = payload.get('match_reason', 'Manual inspection pairing')

    success, result, status_code = manual_match_items(lost_id, found_id, reason, current_user)
    return jsonify({"success": success, "message": result.get('message'), "data": result}), status_code

# --- RELEASE ITEM ---
@item_bp.route('/found-items/<int:case_id>/release', methods=['POST'])
@token_required
@role_required(['POLICE_OFFICER', 'HELP_CENTER_OPERATOR', 'EVENT_ADMIN', 'SUPER_ADMIN'])
def release_item_route(case_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}

    success, result, status_code = release_found_item(case_id, payload, current_user)
    return jsonify({"success": success, "message": result.get('message')}), status_code

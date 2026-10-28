from flask import Blueprint, request, jsonify
from utils.auth import token_required, role_required
from services.dindi_service import (
    create_dindi, get_dindi_details, list_dindis,
    add_dindi_member, list_dindi_members, assign_dindi_leader,
    create_dindi_schedule, create_dindi_announcement, verify_dindi
)
from db import execute_query

dindi_bp = Blueprint('dindis', __name__, url_prefix='/api')

# --- DINDIS ---
@dindi_bp.route('/dindis', methods=['POST'])
@token_required
@role_required(['DINDI_LEADER', 'EVENT_ADMIN', 'SUPER_ADMIN'])
def create_dindi_route():
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}

    success, result, status_code = create_dindi(payload, current_user)
    return jsonify({"success": success, "message": result.get('message', 'Dindi created.'), "data": result}), status_code

@dindi_bp.route('/dindis', methods=['GET'])
@token_required
def get_dindis_route():
    number = request.args.get('number')
    name = request.args.get('name')
    status = request.args.get('status')

    dindis = list_dindis(number=number, name=name, status=status)
    return jsonify({"success": True, "message": "Dindis retrieved.", "data": dindis}), 200

@dindi_bp.route('/dindis/<int:dindi_id>', methods=['GET'])
@token_required
def get_dindi_by_id_route(dindi_id):
    dindi = get_dindi_details(dindi_id)
    if not dindi:
        return jsonify({"success": False, "message": "Dindi not found.", "error_code": "NOT_FOUND"}), 404
    return jsonify({"success": True, "message": "Dindi details retrieved.", "data": dindi}), 200

# --- MEMBERS ---
@dindi_bp.route('/dindis/<int:dindi_id>/members', methods=['POST'])
@token_required
@role_required(['DINDI_LEADER', 'EVENT_ADMIN', 'SUPER_ADMIN'])
def add_dindi_member_route(dindi_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}
    person_id = payload.get('person_id')
    role = payload.get('role', 'MEMBER')

    if not person_id:
        return jsonify({"success": False, "message": "person_id is required."}), 400

    success, result, status_code = add_dindi_member(dindi_id, person_id, role, current_user)
    return jsonify({"success": success, "message": result.get('message'), "data": result}), status_code

@dindi_bp.route('/dindis/<int:dindi_id>/members', methods=['GET'])
@token_required
def get_dindi_members_route(dindi_id):
    members = list_dindi_members(dindi_id)
    return jsonify({"success": True, "message": "Dindi members retrieved.", "data": members}), 200

# --- LEADERS ---
@dindi_bp.route('/dindis/<int:dindi_id>/leaders', methods=['POST'])
@token_required
@role_required(['EVENT_ADMIN', 'SUPER_ADMIN'])
def assign_dindi_leader_route(dindi_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}
    user_id = payload.get('user_id')
    role = payload.get('role', 'ASSISTANT_LEADER')

    success, result, status_code = assign_dindi_leader(dindi_id, user_id, role, current_user)
    return jsonify({"success": success, "message": result.get('message'), "data": result}), status_code

# --- SCHEDULE ---
@dindi_bp.route('/dindis/<int:dindi_id>/schedule', methods=['POST'])
@token_required
@role_required(['DINDI_LEADER', 'EVENT_ADMIN', 'SUPER_ADMIN'])
def create_dindi_schedule_route(dindi_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}

    success, result, status_code = create_dindi_schedule(dindi_id, payload, current_user)
    return jsonify({"success": success, "message": result.get('message'), "data": result}), status_code

# --- ANNOUNCEMENTS ---
@dindi_bp.route('/dindis/<int:dindi_id>/announcements', methods=['POST'])
@token_required
@role_required(['DINDI_LEADER', 'EVENT_ADMIN', 'SUPER_ADMIN'])
def create_dindi_announcement_route(dindi_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}

    success, result, status_code = create_dindi_announcement(dindi_id, payload, current_user)
    return jsonify({"success": success, "message": result.get('message'), "data": result}), status_code

# --- VERIFICATION ---
@dindi_bp.route('/dindis/<int:dindi_id>/verify', methods=['POST'])
@token_required
@role_required(['EVENT_ADMIN', 'SUPER_ADMIN'])
def verify_dindi_route(dindi_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}

    success, result, status_code = verify_dindi(dindi_id, payload, current_user)
    return jsonify({"success": success, "message": result.get('message')}), status_code

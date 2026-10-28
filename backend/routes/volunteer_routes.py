from flask import Blueprint, request, jsonify
from utils.auth import token_required, role_required
from services.volunteer_service import (
    register_volunteer, verify_volunteer, get_volunteer_details, list_volunteers,
    create_volunteer_task, get_task_details, generate_task_recommendations,
    assign_task, accept_task, decline_task, complete_task, verify_task_completion,
    volunteer_check_in, volunteer_check_out
)
from db import execute_query

vol_bp = Blueprint('volunteers', __name__, url_prefix='/api')

# --- VOLUNTEERS ---
@vol_bp.route('/volunteers', methods=['POST'])
@token_required
def register_volunteer_route():
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}
    success, result, status_code = register_volunteer(payload, current_user)
    return jsonify({"success": success, "message": result.get('message', 'Volunteer registered.'), "data": result}), status_code

@vol_bp.route('/volunteers', methods=['GET'])
@token_required
def get_volunteers_route():
    zone = request.args.get('zone')
    status = request.args.get('status')
    volunteers = list_volunteers(zone=zone, status=status)
    return jsonify({"success": True, "message": "Volunteers retrieved.", "data": volunteers}), 200

@vol_bp.route('/volunteers/<int:vol_id>', methods=['GET'])
@token_required
def get_volunteer_by_id_route(vol_id):
    vol = get_volunteer_details(vol_id)
    if not vol:
        return jsonify({"success": False, "message": "Volunteer not found."}), 404
    return jsonify({"success": True, "message": "Volunteer details retrieved.", "data": vol}), 200

@vol_bp.route('/volunteers/<int:vol_id>/status', methods=['PATCH'])
@token_required
@role_required(['EVENT_ADMIN', 'SUPER_ADMIN'])
def verify_volunteer_route(vol_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}
    status = payload.get('status', 'VERIFIED')
    notes = payload.get('verification_notes', '')

    success, result, status_code = verify_volunteer(vol_id, status, notes, current_user)
    return jsonify({"success": success, "message": result.get('message')}), status_code

# --- ATTENDANCE ---
@vol_bp.route('/volunteers/<int:vol_id>/check-in', methods=['POST'])
@token_required
def volunteer_check_in_route(vol_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}
    shift_id = payload.get('shift_id', 1)

    success, result, status_code = volunteer_check_in(vol_id, shift_id, current_user)
    return jsonify({"success": success, "message": result.get('message'), "data": result}), status_code

@vol_bp.route('/volunteers/<int:vol_id>/check-out', methods=['POST'])
@token_required
def volunteer_check_out_route(vol_id):
    current_user = getattr(request, 'current_user', {})
    success, result, status_code = volunteer_check_out(vol_id, current_user)
    return jsonify({"success": success, "message": result.get('message')}), status_code

# --- TASKS ---
@vol_bp.route('/volunteer-tasks', methods=['POST'])
@token_required
@role_required(['EVENT_ADMIN', 'SUPER_ADMIN', 'HELP_CENTER_OPERATOR', 'POLICE_OFFICER', 'MEDICAL_STAFF', 'DINDI_LEADER'])
def create_task_route():
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}
    success, result, status_code = create_volunteer_task(payload, current_user)
    return jsonify({"success": success, "message": result.get('message'), "data": result}), status_code

@vol_bp.route('/volunteer-tasks', methods=['GET'])
@token_required
def get_tasks_route():
    tasks = execute_query("SELECT * FROM volunteer_tasks ORDER BY id DESC", fetchall=True) or []
    return jsonify({"success": True, "message": "Volunteer tasks retrieved.", "data": tasks}), 200

@vol_bp.route('/volunteer-tasks/<int:task_id>', methods=['GET'])
@token_required
def get_task_by_id_route(task_id):
    task = get_task_details(task_id)
    if not task:
        return jsonify({"success": False, "message": "Task not found."}), 404
    return jsonify({"success": True, "message": "Task details retrieved.", "data": task}), 200

# --- RECOMMENDATIONS & ASSIGNMENT ---
@vol_bp.route('/volunteer-tasks/<int:task_id>/recommendations', methods=['GET'])
@token_required
def get_task_recommendations_route(task_id):
    recs = generate_task_recommendations(task_id)
    return jsonify({"success": True, "message": "Rule-based task assignment recommendations generated.", "data": recs}), 200

@vol_bp.route('/volunteer-tasks/<int:task_id>/assign', methods=['POST'])
@token_required
@role_required(['EVENT_ADMIN', 'SUPER_ADMIN', 'HELP_CENTER_OPERATOR', 'POLICE_OFFICER'])
def assign_task_route(task_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}
    vol_id = payload.get('volunteer_id')

    if not vol_id:
        return jsonify({"success": False, "message": "volunteer_id is required."}), 400

    success, result, status_code = assign_task(task_id, vol_id, current_user)
    return jsonify({"success": success, "message": result.get('message')}), status_code

@vol_bp.route('/volunteer-tasks/<int:task_id>/accept', methods=['POST'])
@token_required
def accept_task_route(task_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}
    vol_id = payload.get('volunteer_id', 1)

    success, result, status_code = accept_task(task_id, vol_id, current_user)
    return jsonify({"success": success, "message": result.get('message')}), status_code

@vol_bp.route('/volunteer-tasks/<int:task_id>/decline', methods=['POST'])
@token_required
def decline_task_route(task_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}
    vol_id = payload.get('volunteer_id', 1)
    reason = payload.get('decline_reason', 'Busy with another task')

    success, result, status_code = decline_task(task_id, vol_id, reason, current_user)
    return jsonify({"success": success, "message": result.get('message')}), status_code

@vol_bp.route('/volunteer-tasks/<int:task_id>/complete', methods=['POST'])
@token_required
def complete_task_route(task_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}
    vol_id = payload.get('volunteer_id', 1)
    notes = payload.get('completion_notes', '')

    success, result, status_code = complete_task(task_id, vol_id, notes, current_user)
    return jsonify({"success": success, "message": result.get('message')}), status_code

@vol_bp.route('/volunteer-tasks/<int:task_id>/verify', methods=['POST'])
@token_required
@role_required(['EVENT_ADMIN', 'SUPER_ADMIN', 'HELP_CENTER_OPERATOR', 'POLICE_OFFICER'])
def verify_task_route(task_id):
    current_user = getattr(request, 'current_user', {})
    success, result, status_code = verify_task_completion(task_id, current_user)
    return jsonify({"success": success, "message": result.get('message')}), status_code

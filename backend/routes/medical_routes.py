from flask import Blueprint, request, jsonify
from utils.auth import token_required, role_required
from services.medical_service import create_medical_case, get_medical_case_details, list_medical_cases, update_case_status
from services.facility_service import list_medical_facilities, get_facility_by_id, find_nearby_facilities
from services.ambulance_service import list_ambulances, request_ambulance, assign_ambulance
from db import execute_query
from services.audit_service import log_audit_event

medical_bp = Blueprint('medical', __name__, url_prefix='/api/medical')

@medical_bp.route('/cases', methods=['POST'])
@token_required
def report_case():
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}
    success, result, status_code = create_medical_case(payload, current_user)
    if success:
        return jsonify({"success": True, "message": "Medical emergency reported successfully.", "data": result}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code')}), status_code

@medical_bp.route('/cases', methods=['GET'])
@token_required
def get_cases():
    current_user = getattr(request, 'current_user', {})
    status = request.args.get('status')
    priority = request.args.get('priority')
    zone = request.args.get('zone')
    my_cases_only = request.args.get('my_cases')

    user_id_filter = current_user['user_id'] if my_cases_only else None
    cases = list_medical_cases(status=status, priority=priority, zone=zone, user_id=user_id_filter)
    return jsonify({"success": True, "message": "Medical cases retrieved.", "data": cases}), 200

@medical_bp.route('/cases/<int:case_id>', methods=['GET'])
@token_required
def get_case_by_id(case_id):
    current_user = getattr(request, 'current_user', {})
    case = get_medical_case_details(case_id, current_user)
    if not case:
        return jsonify({"success": False, "message": "Medical case not found.", "error_code": "NOT_FOUND"}), 404
    return jsonify({"success": True, "message": "Medical case details retrieved.", "data": case}), 200

@medical_bp.route('/cases/<int:case_id>/status', methods=['PATCH'])
@token_required
def patch_case_status(case_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}
    new_status = payload.get('status')
    reason = payload.get('reason')

    success, result, status_code = update_case_status(case_id, new_status, reason, current_user)
    if success:
        return jsonify({"success": True, "message": result.get('message'), "data": result}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code')}), status_code

@medical_bp.route('/cases/<int:case_id>/ambulance', methods=['POST'])
@token_required
def handle_ambulance_request(case_id):
    current_user = getattr(request, 'current_user', {})
    success, result, status_code = request_ambulance(case_id, current_user)
    if success:
        return jsonify({"success": True, "message": result.get('message'), "data": result}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code')}), status_code

@medical_bp.route('/cases/<int:case_id>/assign', methods=['POST'])
@token_required
@role_required(['DOCTOR', 'NURSE', 'PARAMEDIC', 'MEDICAL_STAFF', 'MEDICAL_COORDINATOR', 'EVENT_ADMIN', 'SUPER_ADMIN'])
def handle_assign_ambulance(case_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}
    ambulance_id = payload.get('ambulance_id')

    if not ambulance_id:
        return jsonify({"success": False, "message": "Ambulance ID is required.", "error_code": "MISSING_AMBULANCE"}), 400

    success, result, status_code = assign_ambulance(case_id, ambulance_id, current_user)
    if success:
        return jsonify({"success": True, "message": result.get('message'), "data": result}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code')}), status_code

@medical_bp.route('/cases/<int:case_id>/treatment', methods=['POST'])
@token_required
@role_required(['DOCTOR', 'NURSE', 'PARAMEDIC', 'MEDICAL_STAFF', 'MEDICAL_COORDINATOR', 'SUPER_ADMIN'])
def record_treatment(case_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}

    assessment = payload.get('assessment', '').strip()
    treatment_provided = payload.get('treatment_provided', '').strip()
    medication = payload.get('medication', '').strip()
    observation = payload.get('observation', '').strip()
    facility_id = payload.get('facility_id', 3)

    if not assessment or not treatment_provided:
        return jsonify({"success": False, "message": "Assessment and Treatment Provided are required fields.", "error_code": "INVALID_INPUT"}), 400

    # Get staff ID for user
    staff = execute_query("SELECT id FROM medical_staff WHERE user_id = %s", (current_user['user_id'],), fetchone=True)
    staff_id = staff['id'] if staff else 1

    treatment_id = execute_query("""
    INSERT INTO medical_treatments (case_id, medical_staff_id, facility_id, assessment, treatment_provided, medication, observation)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (case_id, staff_id, facility_id, assessment, treatment_provided, medication, observation), commit=True)

    # Update case status to TREATMENT
    execute_query("UPDATE medical_cases SET status = 'TREATMENT', updated_at = NOW() WHERE id = %s", (case_id,), commit=True)

    log_audit_event(
        user_id=current_user['user_id'],
        action="MEDICAL_TREATMENT_RECORDED",
        details={"case_id": case_id, "treatment_id": treatment_id, "staff_id": staff_id}
    )

    return jsonify({"success": True, "message": "Medical treatment recorded successfully.", "data": {"treatment_id": treatment_id}}), 201

@medical_bp.route('/cases/<int:case_id>/referral', methods=['POST'])
@token_required
@role_required(['DOCTOR', 'NURSE', 'PARAMEDIC', 'MEDICAL_STAFF', 'MEDICAL_COORDINATOR', 'SUPER_ADMIN'])
def record_referral(case_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}

    to_facility = payload.get('to_facility_name', '').strip()
    reason = payload.get('reason', '').strip()
    from_facility_id = payload.get('from_facility_id', 3)
    ambulance_req = 1 if payload.get('ambulance_required') else 0

    if not to_facility or not reason:
        return jsonify({"success": False, "message": "Target hospital name and referral reason are required.", "error_code": "INVALID_INPUT"}), 400

    ref_id = execute_query("""
    INSERT INTO medical_referrals (case_id, from_facility_id, to_facility_name, reason, ambulance_required, referred_at, status)
    VALUES (%s, %s, %s, %s, %s, NOW(), 'REFERRED')
    """, (case_id, from_facility_id, to_facility, reason, ambulance_req), commit=True)

    # Update case status to REFERRED
    execute_query("UPDATE medical_cases SET status = 'REFERRED', updated_at = NOW() WHERE id = %s", (case_id,), commit=True)

    log_audit_event(
        user_id=current_user['user_id'],
        action="MEDICAL_REFERRAL_CREATED",
        details={"case_id": case_id, "referral_id": ref_id, "to_facility": to_facility}
    )

    return jsonify({"success": True, "message": "Hospital referral created successfully.", "data": {"referral_id": ref_id}}), 201

# Facilities & Ambulances Routes
@medical_bp.route('/facilities', methods=['GET'])
def get_facilities():
    zone = request.args.get('zone')
    fac_type = request.args.get('type')
    status = request.args.get('status')
    facilities = list_medical_facilities(zone=zone, facility_type=fac_type, status=status)
    return jsonify({"success": True, "message": "Medical facilities retrieved.", "data": facilities}), 200

@medical_bp.route('/facilities/nearby', methods=['GET'])
def get_nearby_facilities_route():
    lat = float(request.args.get('lat', 18.3444))
    lon = float(request.args.get('lon', 74.0306))
    zone = request.args.get('zone')
    facilities = find_nearby_facilities(lat, lon, zone=zone)
    return jsonify({"success": True, "message": "Nearby medical facilities retrieved.", "data": facilities}), 200

@medical_bp.route('/ambulances', methods=['GET'])
def get_ambulances():
    status = request.args.get('status')
    ambulances = list_ambulances(status=status)
    return jsonify({"success": True, "message": "Ambulances retrieved.", "data": ambulances}), 200

@medical_bp.route('/dashboard', methods=['GET'])
@token_required
def get_medical_dashboard():
    current_user = getattr(request, 'current_user', {})
    
    total_cases = execute_query("SELECT COUNT(*) as cnt FROM medical_cases", fetchone=True)['cnt']
    critical_cases = execute_query("SELECT COUNT(*) as cnt FROM medical_cases WHERE priority_level = 'CRITICAL' AND status NOT IN ('RESOLVED', 'CLOSED', 'CANCELLED')", fetchone=True)['cnt']
    active_cases = execute_query("SELECT COUNT(*) as cnt FROM medical_cases WHERE status NOT IN ('RESOLVED', 'CLOSED', 'CANCELLED')", fetchone=True)['cnt']
    ambulances_avail = execute_query("SELECT COUNT(*) as cnt FROM ambulances WHERE status = 'AVAILABLE'", fetchone=True)['cnt']
    camps_avail = execute_query("SELECT COUNT(*) as cnt FROM medical_facilities WHERE status = 'AVAILABLE'", fetchone=True)['cnt']
    referrals_pending = execute_query("SELECT COUNT(*) as cnt FROM medical_referrals WHERE status = 'REFERRED'", fetchone=True)['cnt']

    return jsonify({
        "success": True,
        "message": "Medical dashboard summary retrieved.",
        "data": {
            "total_cases": total_cases,
            "active_cases": active_cases,
            "critical_cases": critical_cases,
            "ambulances_available": ambulances_avail,
            "camps_available": camps_avail,
            "referrals_pending": referrals_pending
        }
    }), 200

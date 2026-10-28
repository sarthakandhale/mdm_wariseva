import uuid
from db import execute_query
from services.audit_service import log_audit_event
from services.facility_service import calculate_haversine_distance

def list_ambulances(status=None):
    where_str = " WHERE status = %s" if status else ""
    params = (status,) if status else ()
    query = f"SELECT * FROM ambulances {where_str} ORDER BY id ASC"
    return execute_query(query, params, fetchall=True)

def request_ambulance(case_id, current_user):
    case = execute_query("SELECT * FROM medical_cases WHERE id = %s", (case_id,), fetchone=True)
    if not case:
        return False, {"message": "Medical case not found.", "error_code": "NOT_FOUND"}, 404

    # Check if request already pending
    existing = execute_query("SELECT id FROM ambulance_assignments WHERE case_id = %s AND status IN ('REQUESTED', 'ASSIGNED', 'DISPATCHED')", (case_id,), fetchone=True)
    if existing:
        return True, {"message": "Ambulance request is already active for this case.", "assignment_id": existing['id']}, 200

    assign_id = execute_query("""
    INSERT INTO ambulance_assignments (ambulance_id, case_id, assigned_by, assigned_at, status)
    VALUES (1, %s, %s, NOW(), 'REQUESTED')
    """, (case_id, current_user['user_id']), commit=True)

    log_audit_event(
        user_id=current_user['user_id'],
        action="AMBULANCE_REQUESTED",
        details={"case_id": case_id, "case_number": case['case_number'], "assignment_id": assign_id}
    )

    return True, {"message": "Ambulance requested successfully.", "assignment_id": assign_id}, 201

def assign_ambulance(case_id, ambulance_id, current_user):
    case = execute_query("SELECT * FROM medical_cases WHERE id = %s", (case_id,), fetchone=True)
    if not case:
        return False, {"message": "Medical case not found.", "error_code": "NOT_FOUND"}, 404

    ambulance = execute_query("SELECT * FROM ambulances WHERE id = %s", (ambulance_id,), fetchone=True)
    if not ambulance:
        return False, {"message": "Ambulance not found.", "error_code": "NOT_FOUND"}, 404

    # Update ambulance status to ASSIGNED
    execute_query("UPDATE ambulances SET status = 'ASSIGNED', updated_at = NOW() WHERE id = %s", (ambulance_id,), commit=True)

    # Insert / Update assignment
    assign_id = execute_query("""
    INSERT INTO ambulance_assignments (ambulance_id, case_id, assigned_by, assigned_at, dispatch_time, status)
    VALUES (%s, %s, %s, NOW(), NOW(), 'DISPATCHED')
    """, (ambulance_id, case_id, current_user['user_id']), commit=True)

    # Update Case Status to ASSIGNED
    execute_query("UPDATE medical_cases SET status = 'ASSIGNED', updated_at = NOW() WHERE id = %s", (case_id,), commit=True)

    log_audit_event(
        user_id=current_user['user_id'],
        action="AMBULANCE_ASSIGNED",
        details={"case_id": case_id, "ambulance_id": ambulance_id, "ambulance_code": ambulance['ambulance_code']}
    )

    return True, {
        "message": f"Ambulance {ambulance['ambulance_code']} dispatched to case {case['case_number']}.",
        "ambulance_code": ambulance['ambulance_code'],
        "driver_name": ambulance['driver_name'],
        "driver_contact": ambulance['driver_contact']
    }, 200

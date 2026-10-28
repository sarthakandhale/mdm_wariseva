import uuid
from datetime import datetime
from db import execute_query
from services.audit_service import log_audit_event
from services.priority_engine import calculate_medical_priority
from services.person_service import get_person_full_profile

def generate_medical_case_code():
    """Generates unique Case Number: WS-MED-2026-XXXXXX"""
    res = execute_query("SELECT COUNT(*) as cnt FROM medical_cases", fetchone=True)
    next_num = (res['cnt'] if res else 0) + 1
    return f"WS-MED-2026-{next_num:06d}"

def generate_temp_patient_code():
    """Generates unique Temporary Patient Code: TEMP-PAT-2026-XXXXX"""
    res = execute_query("SELECT COUNT(*) as cnt FROM medical_cases WHERE temp_patient_code IS NOT NULL", fetchone=True)
    next_num = (res['cnt'] if res else 0) + 1
    return f"TEMP-PAT-2026-{next_num:05d}"

def create_medical_case(payload, current_user):
    """
    Creates a new medical emergency case.
    Integrates with Module 2 for registered family/self profiles,
    or generates a temporary patient ID for unidentified victims.
    """
    user_id = current_user['user_id']
    emergency_type = payload.get('emergency_type', 'OTHER').upper()
    reported_severity = payload.get('reported_severity', 'MEDIUM').upper()
    description = payload.get('description', '').strip()

    # Patient Selection Logic
    patient_person_id = payload.get('patient_person_id')
    temp_code = None
    temp_name = None
    temp_age = None
    temp_gender = None
    temp_desc = None
    patient_age = None
    is_child = False
    is_elderly = False
    med_history = None

    if patient_person_id:
        person = get_person_full_profile(patient_person_id)
        if person:
            patient_age = person.get('calculated_age')
            is_child = (person.get('age_category') == 'CHILD')
            is_elderly = (person.get('age_category') == 'ELDERLY')
            med_history = person.get('safety', {}).get('medical_condition')
    else:
        # Unidentified or temporary patient
        temp_code = generate_temp_patient_code()
        temp_name = payload.get('temp_patient_name', 'Unidentified Pilgrim').strip()
        temp_age = int(payload.get('temp_patient_age', 30)) if payload.get('temp_patient_age') else 30
        temp_gender = payload.get('temp_patient_gender', 'MALE').upper()
        temp_desc = payload.get('temp_patient_description', '').strip()
        patient_age = temp_age
        is_child = (temp_age <= 12)
        is_elderly = (temp_age >= 60)

    # Symptoms list
    symptoms = payload.get('symptoms', [])
    if isinstance(symptoms, str):
        symptoms = [s.strip() for s in symptoms.split(',') if s.strip()]

    is_unconscious = payload.get('is_unconscious', False) or 'Unconsciousness' in symptoms or emergency_type == 'FAINTING'
    zone = payload.get('zone', 'Alandi').strip()

    # Calculate System Priority Score & Level via Priority Engine
    score, level, reasons = calculate_medical_priority(
        emergency_type=emergency_type,
        symptoms=symptoms,
        age=patient_age,
        is_child=is_child,
        is_elderly=is_elderly,
        medical_history=med_history,
        location_zone=zone,
        is_unconscious=is_unconscious
    )

    case_number = generate_medical_case_code()
    case_uuid = f"mc-{uuid.uuid4().hex[:12]}"

    sql = """
    INSERT INTO medical_cases (
        uuid, case_number, patient_person_id, temp_patient_code, temp_patient_name,
        temp_patient_age, temp_patient_gender, temp_patient_description, reported_by_user_id,
        emergency_type, reported_severity, priority_score, priority_level, priority_reasons,
        description, medical_attention_required, status
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1, 'REPORTED')
    """
    case_id = execute_query(sql, (
        case_uuid, case_number, patient_person_id, temp_code, temp_name,
        temp_age, temp_gender, temp_desc, user_id,
        emergency_type, reported_severity, score, level, reasons, description
    ), commit=True)

    # Insert Location Record
    execute_query("""
    INSERT INTO medical_case_locations (
        case_id, zone, route, landmark, latitude, longitude, location_description, location_source
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        case_id, zone, payload.get('route', 'Alandi-Pandharpur Route'),
        payload.get('landmark'), payload.get('latitude'), payload.get('longitude'),
        payload.get('location_description'), payload.get('location_source', 'MANUAL')
    ), commit=True)

    # Insert Symptoms
    sym_severity = 'HIGH' if level in ['HIGH', 'CRITICAL'] else 'MODERATE'
    for sym in symptoms:
        execute_query("""
        INSERT INTO medical_case_symptoms (case_id, symptom, severity)
        VALUES (%s, %s, %s)
        """, (case_id, sym, sym_severity), commit=True)


    # Initial Status History
    execute_query("""
    INSERT INTO medical_case_status_history (case_id, old_status, new_status, changed_by, reason)
    VALUES (%s, NULL, 'REPORTED', %s, 'Emergency case filed')
    """, (case_id, user_id), commit=True)

    # Log Audit Event
    log_audit_event(
        user_id=user_id,
        action="MEDICAL_CASE_CREATED",
        details={"case_id": case_id, "case_number": case_number, "emergency_type": emergency_type, "priority_level": level, "score": score}
    )

    return True, get_medical_case_details(case_id, current_user), 201

def get_medical_case_details(case_id, current_user=None):
    """
    Retrieves complete medical case details, location, symptoms, staff, treatment, and referrals.
    """
    case = execute_query("""
    SELECT 
        c.*, u.full_name as reporter_name, u.mobile as reporter_mobile, u.email as reporter_email
    FROM medical_cases c
    JOIN users u ON c.reported_by_user_id = u.id
    WHERE c.id = %s
    """, (case_id,), fetchone=True)

    if not case:
        return None

    # Patient info
    if case['patient_person_id']:
        person = get_person_full_profile(case['patient_person_id'], current_user)
        case['patient'] = person
    else:
        case['patient'] = {
            'temp_patient_code': case['temp_patient_code'],
            'full_name': case['temp_patient_name'],
            'calculated_age': case['temp_patient_age'],
            'gender': case['temp_patient_gender'],
            'description': case['temp_patient_description'],
            'is_temporary': True
        }

    # Location
    location = execute_query("SELECT * FROM medical_case_locations WHERE case_id = %s", (case_id,), fetchone=True)
    case['location'] = location or {}

    # Symptoms
    symptoms = execute_query("SELECT symptom, severity FROM medical_case_symptoms WHERE case_id = %s", (case_id,), fetchall=True)
    case['symptoms'] = [s['symptom'] for s in symptoms] if symptoms else []

    # Treatments (Restricted to Authorized Medical Personnel / Admins)
    is_medical_role = current_user and current_user['role_name'] in ['DOCTOR', 'NURSE', 'PARAMEDIC', 'MEDICAL_STAFF', 'MEDICAL_COORDINATOR', 'SUPER_ADMIN', 'EVENT_ADMIN']
    if is_medical_role:
        treatments = execute_query("""
        SELECT t.*, ms.staff_code, ms.qualification, f.name as facility_name
        FROM medical_treatments t
        JOIN medical_staff ms ON t.medical_staff_id = ms.id
        JOIN medical_facilities f ON t.facility_id = f.id
        WHERE t.case_id = %s
        ORDER BY t.created_at DESC
        """, (case_id,), fetchall=True)
        case['treatments'] = treatments or []
    else:
        case['treatments'] = [] # Masked for non-medical users

    # Referrals
    referrals = execute_query("SELECT * FROM medical_referrals WHERE case_id = %s ORDER BY id DESC", (case_id,), fetchall=True)
    case['referrals'] = referrals or []

    # Ambulance Assignments
    assignments = execute_query("""
    SELECT aa.*, a.ambulance_code, a.registration_number, a.driver_name, a.driver_contact
    FROM ambulance_assignments aa
    JOIN ambulances a ON aa.ambulance_id = a.id
    WHERE aa.case_id = %s
    ORDER BY aa.id DESC
    """, (case_id,), fetchall=True)
    case['ambulance_assignments'] = assignments or []

    # Status Timeline History
    history = execute_query("SELECT * FROM medical_case_status_history WHERE case_id = %s ORDER BY id ASC", (case_id,), fetchall=True)
    case['timeline'] = history or []

    return case

def list_medical_cases(status=None, priority=None, zone=None, user_id=None, limit=50, offset=0):
    """
    Lists medical cases with optional filters.
    """
    where_clauses = []
    params = []

    if status:
        where_clauses.append("c.status = %s")
        params.append(status)

    if priority:
        where_clauses.append("c.priority_level = %s")
        params.append(priority)

    if zone:
        where_clauses.append("l.zone = %s")
        params.append(zone)

    if user_id:
        where_clauses.append("c.reported_by_user_id = %s")
        params.append(user_id)

    where_str = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    query = f"""
    SELECT 
        c.id, c.uuid, c.case_number, c.emergency_type, c.reported_severity,
        c.priority_score, c.priority_level, c.priority_reasons, c.status, c.created_at,
        c.patient_person_id, c.temp_patient_code, c.temp_patient_name, c.temp_patient_age,
        l.zone, l.landmark, l.location_description
    FROM medical_cases c
    LEFT JOIN medical_case_locations l ON c.id = l.case_id
    {where_str}
    ORDER BY FIELD(c.priority_level, 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'), c.created_at DESC
    LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])
    cases = execute_query(query, tuple(params), fetchall=True)
    return cases

def update_case_status(case_id, new_status, reason, current_user):
    """
    Transitions emergency case status with audit logging.
    """
    case = execute_query("SELECT status FROM medical_cases WHERE id = %s", (case_id,), fetchone=True)
    if not case:
        return False, {"message": "Medical case not found.", "error_code": "NOT_FOUND"}, 404

    old_status = case['status']
    valid_statuses = ['REPORTED', 'TRIAGE', 'ASSIGNED', 'RESPONDING', 'ARRIVED', 'TREATMENT', 'REFERRED', 'OBSERVATION', 'RESOLVED', 'CANCELLED', 'CLOSED']

    if new_status not in valid_statuses:
        return False, {"message": f"Invalid status: {new_status}", "error_code": "INVALID_STATUS"}, 400

    close_clause = ", closed_at = NOW()" if new_status in ['RESOLVED', 'CLOSED', 'CANCELLED'] else ""
    execute_query(f"UPDATE medical_cases SET status = %s, updated_at = NOW() {close_clause} WHERE id = %s", (new_status, case_id), commit=True)

    execute_query("""
    INSERT INTO medical_case_status_history (case_id, old_status, new_status, changed_by, reason)
    VALUES (%s, %s, %s, %s, %s)
    """, (case_id, old_status, new_status, current_user['user_id'], reason or f"Status updated to {new_status}"), commit=True)

    log_audit_event(
        user_id=current_user['user_id'],
        action="MEDICAL_CASE_STATUS_CHANGED",
        details={"case_id": case_id, "old_status": old_status, "new_status": new_status, "reason": reason}
    )

    return True, {"message": f"Case status updated from {old_status} to {new_status}.", "new_status": new_status}, 200

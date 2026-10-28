import uuid
from datetime import datetime
from db import execute_query
from services.audit_service import log_audit_event
from services.lost_priority_engine import calculate_lost_person_priority
from services.person_service import get_person_full_profile

def generate_lost_case_code():
    """Generates unique Case Number: WS-LP-2026-XXXXXX"""
    res = execute_query("SELECT COUNT(*) as cnt FROM lost_person_cases", fetchone=True)
    next_num = (res['cnt'] if res else 0) + 1
    return f"WS-LP-2026-{next_num:06d}"

def generate_temp_person_code():
    """Generates unique Temporary Person Code: TEMP-PER-2026-XXXXX"""
    res = execute_query("SELECT COUNT(*) as cnt FROM lost_person_cases WHERE temp_person_code IS NOT NULL", fetchone=True)
    next_num = (res['cnt'] if res else 0) + 1
    return f"TEMP-PER-2026-{next_num:05d}"

def check_active_lost_case_for_person(person_id):
    """
    Checks if person already has an active lost person case.
    Active statuses: REPORTED, UNDER_REVIEW, SEARCHING, POSSIBLE_SIGHTING, POSSIBLE_MATCH, VERIFICATION
    """
    if not person_id:
        return None

    query = """
    SELECT id, case_number, status, priority_level, created_at
    FROM lost_person_cases
    WHERE person_id = %s AND status IN ('REPORTED', 'UNDER_REVIEW', 'SEARCHING', 'POSSIBLE_SIGHTING', 'POSSIBLE_MATCH', 'VERIFICATION')
    ORDER BY id DESC LIMIT 1
    """
    return execute_query(query, (person_id,), fetchone=True)

def create_lost_person_case(payload, current_user):
    """
    Files a new lost person missing case with duplicate check, priority engine,
    location, clothing, and initial audit log.
    """
    user_id = current_user['user_id']
    person_id = payload.get('person_id')
    family_id = payload.get('family_id')

    # 1. Duplicate Active Case Check
    if person_id:
        active_case = check_active_lost_case_for_person(person_id)
        if active_case:
            return False, {
                "message": f"This person already has an active lost-person case (#{active_case['case_number']}). Status: {active_case['status']}.",
                "error_code": "DUPLICATE_ACTIVE_CASE",
                "active_case": active_case
            }, 409

    temp_code = None
    temp_name = None
    temp_age = None
    temp_gender = None
    temp_desc = None
    patient_age = None
    is_child = False
    is_elderly = False
    med_req = False
    cog_aid = False
    comm_diff = False

    if person_id:
        person = get_person_full_profile(person_id, current_user)
        if person:
            patient_age = person.get('calculated_age')
            is_child = (person.get('age_category') == 'CHILD')
            is_elderly = (person.get('age_category') == 'ELDERLY')
            safety = person.get('safety', {})
            med_req = bool(safety.get('medical_condition') or safety.get('medication_requirement'))
            cog_aid = bool(safety.get('cognitive_assistance_required'))
            comm_diff = bool(safety.get('communication_difficulty'))
    else:
        # Unregistered / Non-family temporary profile
        temp_code = generate_temp_person_code()
        temp_name = payload.get('temp_person_name', 'Unregistered Missing Pilgrim').strip()
        temp_age = int(payload.get('temp_person_age', 30)) if payload.get('temp_person_age') else 30
        temp_gender = payload.get('temp_person_gender', 'MALE').upper()
        temp_desc = payload.get('temp_person_description', '').strip()
        patient_age = temp_age
        is_child = (temp_age <= 12)
        is_elderly = (temp_age >= 60)

    # Calculate Priority
    zone = payload.get('zone', 'Saswad')
    last_seen_str = payload.get('last_seen_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    score, level, reasons = calculate_lost_person_priority(
        age=patient_age,
        is_child=is_child,
        is_elderly=is_elderly,
        medical_requirement=med_req or payload.get('medical_attention_required', False),
        cognitive_assistance=cog_aid or payload.get('cognitive_assistance', False),
        communication_difficulty=comm_diff or payload.get('communication_difficulty', False),
        last_seen_hour=14,
        zone=zone,
        duration_hours=2
    )

    case_number = generate_lost_case_code()
    case_uuid = f"lp-{uuid.uuid4().hex[:12]}"
    reporter_rel = payload.get('reporter_relationship', 'Guardian')
    additional_info = payload.get('additional_information', '').strip()
    medical_req = 1 if payload.get('medical_attention_required') or med_req else 0

    sql = """
    INSERT INTO lost_person_cases (
        uuid, case_number, person_id, temp_person_code, temp_person_name,
        temp_person_age, temp_person_gender, temp_person_description, family_id,
        reported_by_user_id, reporter_relationship, reported_at, last_seen_at,
        priority_score, priority_level, priority_reasons, status, additional_information,
        medical_attention_required
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s, 'REPORTED', %s, %s)
    """
    case_id = execute_query(sql, (
        case_uuid, case_number, person_id, temp_code, temp_name,
        temp_age, temp_gender, temp_desc, family_id,
        user_id, reporter_rel, last_seen_str,
        score, level, reasons, additional_info, medical_req
    ), commit=True)

    # Insert Location Record
    execute_query("""
    INSERT INTO lost_person_locations (
        case_id, zone, route_section, landmark, latitude, longitude, location_description, location_source
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        case_id, zone, payload.get('route_section', 'Alandi-Pandharpur Route'),
        payload.get('landmark'), payload.get('latitude'), payload.get('longitude'),
        payload.get('location_description'), payload.get('location_source', 'MANUAL')
    ), commit=True)

    # Insert Case-Specific Clothing Record (Does NOT mutate permanent person profile)
    c = payload.get('clothing', {})
    execute_query("""
    INSERT INTO lost_person_clothing (
        case_id, top_type, top_color, bottom_type, bottom_color, footwear, footwear_color, headwear, accessories, description, confirmed_from_profile
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        case_id, c.get('top_type', 'T-Shirt'), c.get('top_color', 'Red'),
        c.get('bottom_type', 'Shorts'), c.get('bottom_color', 'Navy Blue'),
        c.get('footwear', 'Sandals'), c.get('footwear_color', 'Brown'),
        c.get('headwear'), c.get('accessories'), c.get('description'),
        1 if c.get('confirmed_from_profile') else 0
    ), commit=True)

    # Initial Status History
    execute_query("""
    INSERT INTO lost_person_status_history (case_id, old_status, new_status, changed_by, reason)
    VALUES (%s, NULL, 'REPORTED', %s, 'Lost person case reported')
    """, (case_id, user_id), commit=True)

    # Log Audit Event
    log_audit_event(
        user_id=user_id,
        action="LOST_CASE_CREATED",
        details={"case_id": case_id, "case_number": case_number, "priority_level": level, "score": score}
    )

    return True, get_lost_person_case_details(case_id, current_user), 201

def get_lost_person_case_details(case_id, current_user=None):
    """
    Retrieves full lost person case details, location, clothing, timeline, notes, and sightings.
    Filters internal notes if caller is ordinary family user.
    """
    case = execute_query("""
    SELECT c.*, u.full_name as reporter_name, u.mobile as reporter_mobile, u.email as reporter_email
    FROM lost_person_cases c
    JOIN users u ON c.reported_by_user_id = u.id
    WHERE c.id = %s
    """, (case_id,), fetchone=True)

    if not case:
        return None

    # Patient / Person Info
    if case['person_id']:
        case['person'] = get_person_full_profile(case['person_id'], current_user)
    else:
        case['person'] = {
            'temp_person_code': case['temp_person_code'],
            'full_name': case['temp_person_name'],
            'calculated_age': case['temp_person_age'],
            'gender': case['temp_person_gender'],
            'description': case['temp_person_description'],
            'is_temporary': True
        }

    # Location
    location = execute_query("SELECT * FROM lost_person_locations WHERE case_id = %s", (case_id,), fetchone=True)
    case['location'] = location or {}

    # Case-specific clothing
    clothing = execute_query("SELECT * FROM lost_person_clothing WHERE case_id = %s", (case_id,), fetchone=True)
    case['clothing'] = clothing or {}

    # Case Notes (Role-based visibility)
    is_staff = current_user and current_user['role_name'] in ['POLICE_OFFICER', 'HELP_CENTER_OPERATOR', 'SUPER_ADMIN', 'EVENT_ADMIN']
    notes_sql = "SELECT n.*, u.full_name as author_name FROM lost_person_notes n JOIN users u ON n.created_by = u.id WHERE n.case_id = %s"
    if not is_staff:
        notes_sql += " AND n.visibility = 'FAMILY_VISIBLE'"
    notes_sql += " ORDER BY n.created_at DESC"
    notes = execute_query(notes_sql, (case_id,), fetchall=True)
    case['notes'] = notes or []

    # Sightings
    sightings = execute_query("""
    SELECT s.*, u.full_name as observer_name, u.mobile as observer_mobile
    FROM lost_person_sightings s
    JOIN users u ON s.reported_by = u.id
    WHERE s.case_id = %s
    ORDER BY s.created_at DESC
    """, (case_id,), fetchall=True)
    case['sightings'] = sightings or []

    # Search Requests
    requests = execute_query("SELECT * FROM lost_person_search_requests WHERE case_id = %s ORDER BY id DESC", (case_id,), fetchall=True)
    case['search_requests'] = requests or []

    # Status Timeline History
    history = execute_query("SELECT * FROM lost_person_status_history WHERE case_id = %s ORDER BY id ASC", (case_id,), fetchall=True)
    case['timeline'] = history or []

    return case

def list_lost_person_cases(status=None, priority=None, zone=None, family_id=None, user_id=None, limit=50, offset=0):
    """
    Lists missing person cases with optional filtering.
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

    if family_id:
        where_clauses.append("c.family_id = %s")
        params.append(family_id)

    if user_id:
        where_clauses.append("c.reported_by_user_id = %s")
        params.append(user_id)

    where_str = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    query = f"""
    SELECT 
        c.id, c.uuid, c.case_number, c.person_id, c.family_id, c.temp_person_code,
        c.temp_person_name, c.temp_person_age, c.priority_score, c.priority_level,
        c.status, c.last_seen_at, c.created_at,
        l.zone, l.landmark, l.location_description
    FROM lost_person_cases c
    LEFT JOIN lost_person_locations l ON c.id = l.case_id
    {where_str}
    ORDER BY FIELD(c.priority_level, 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'), c.created_at DESC
    LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])
    cases = execute_query(query, tuple(params), fetchall=True)
    return cases

def override_case_priority(case_id, new_priority, reason, current_user):
    """
    Allows Police / Help Center operators to override calculated priority.
    """
    case = execute_query("SELECT priority_level, priority_score FROM lost_person_cases WHERE id = %s", (case_id,), fetchone=True)
    if not case:
        return False, {"message": "Case not found.", "error_code": "NOT_FOUND"}, 404

    old_priority = case['priority_level']
    execute_query("""
    UPDATE lost_person_cases
    SET priority_level = %s, is_priority_overridden = 1, override_reason = %s,
        overridden_by = %s, overridden_at = NOW(), updated_at = NOW()
    WHERE id = %s
    """, (new_priority, reason, current_user['user_id'], case_id), commit=True)

    log_audit_event(
        user_id=current_user['user_id'],
        action="LOST_CASE_PRIORITY_CHANGED",
        details={"case_id": case_id, "old_priority": old_priority, "new_priority": new_priority, "reason": reason}
    )

    return True, {"message": f"Priority overridden from {old_priority} to {new_priority}.", "new_priority": new_priority}, 200

def withdraw_lost_person_case(case_id, reason, current_user):
    """
    Allows family guardian to withdraw missing case (e.g. found by family).
    Updates status to WITHDRAWN without deleting records.
    """
    case = execute_query("SELECT status FROM lost_person_cases WHERE id = %s", (case_id,), fetchone=True)
    if not case:
        return False, {"message": "Case not found.", "error_code": "NOT_FOUND"}, 404

    old_status = case['status']
    execute_query("""
    UPDATE lost_person_cases
    SET status = 'WITHDRAWN', updated_at = NOW(), closed_at = NOW()
    WHERE id = %s
    """, (case_id,), commit=True)

    execute_query("""
    INSERT INTO lost_person_status_history (case_id, old_status, new_status, changed_by, reason)
    VALUES (%s, %s, 'WITHDRAWN', %s, %s)
    """, (case_id, old_status, current_user['user_id'], reason or "Case withdrawn by reporter"), commit=True)

    log_audit_event(
        user_id=current_user['user_id'],
        action="LOST_CASE_WITHDRAWN",
        details={"case_id": case_id, "reason": reason}
    )

    return True, {"message": "Lost person report withdrawn successfully."}, 200

def add_case_note(case_id, note_text, visibility, current_user):
    """
    Adds a note to a missing person case with INTERNAL or FAMILY_VISIBLE visibility.
    """
    note_id = execute_query("""
    INSERT INTO lost_person_notes (case_id, created_by, note, visibility)
    VALUES (%s, %s, %s, %s)
    """, (case_id, current_user['user_id'], note_text, visibility or 'FAMILY_VISIBLE'), commit=True)

    return True, {"message": "Case note added.", "note_id": note_id}, 201

def report_sighting(case_id, payload, current_user):
    """
    Submits a possible sighting for a missing person case.
    """
    sighting_id = execute_query("""
    INSERT INTO lost_person_sightings (
        case_id, reported_by, location_description, zone, latitude, longitude, description, photo_path, confidence_rating, status
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'REPORTED')
    """, (
        case_id, current_user['user_id'],
        payload.get('location_description', 'Palkhi Route'),
        payload.get('zone', 'Saswad'),
        payload.get('latitude'), payload.get('longitude'),
        payload.get('description'), payload.get('photo_path'),
        payload.get('confidence_rating', 'MEDIUM')
    ), commit=True)

    # Update case status to POSSIBLE_SIGHTING if currently REPORTED/SEARCHING
    execute_query("UPDATE lost_person_cases SET status = 'POSSIBLE_SIGHTING', updated_at = NOW() WHERE id = %s AND status IN ('REPORTED', 'SEARCHING')", (case_id,), commit=True)

    log_audit_event(
        user_id=current_user['user_id'],
        action="LOST_CASE_SIGHTING_REPORTED",
        details={"case_id": case_id, "sighting_id": sighting_id}
    )

    return True, {"message": "Sighting report submitted successfully.", "sighting_id": sighting_id}, 201

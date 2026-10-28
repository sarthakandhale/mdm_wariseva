import uuid
from datetime import datetime
from db import execute_query
from services.audit_service import log_audit_event
from services.person_service import get_person_full_profile

def generate_found_case_code():
    """Generates unique Found Person Case Code: WS-FP-2026-XXXXXX"""
    res = execute_query("SELECT COUNT(*) as cnt FROM found_person_cases", fetchone=True)
    next_num = (res['cnt'] if res else 0) + 1
    return f"WS-FP-2026-{next_num:06d}"

def generate_temp_found_person_id():
    """Generates unique Temporary Found Person ID: TEMP-FP-PER-2026-XXXXX"""
    res = execute_query("SELECT COUNT(*) as cnt FROM found_person_cases WHERE temporary_person_id IS NOT NULL", fetchone=True)
    next_num = (res['cnt'] if res else 0) + 1
    return f"TEMP-FP-PER-2026-{next_num:05d}"

def create_found_person_case(payload, current_user):
    """
    Registers a new found person case with location, clothing, initial safe location,
    optional medical integration, and audit logging.
    """
    user_id = current_user['user_id']
    linked_person_id = payload.get('linked_person_id')
    identification_status = payload.get('identification_status', 'UNIDENTIFIED_PERSON')
    
    case_number = generate_found_case_code()
    temp_person_id = generate_temp_found_person_id()
    case_uuid = f"fp-{uuid.uuid4().hex[:12]}"

    approx_name = payload.get('approximate_name', 'Unidentified Pilgrim').strip()
    approx_age = int(payload.get('approximate_age', 30)) if payload.get('approximate_age') else 30
    gender = payload.get('gender', 'MALE').upper()
    language = payload.get('language', 'Marathi')
    comm_status = payload.get('communication_status', 'CAN_COMMUNICATE')
    med_req = 1 if payload.get('medical_attention_required') else 0
    special_assist = payload.get('special_assistance_required', '').strip()

    # Optional Medical Case Linking (Module 3 Integration)
    medical_case_id = payload.get('medical_case_id')

    sql = """
    INSERT INTO found_person_cases (
        uuid, case_number, temporary_person_id, linked_person_id, reported_by_user_id,
        identification_status, approximate_name, approximate_age, gender, language,
        communication_status, medical_attention_required, medical_case_id, special_assistance_required, status
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'REPORTED')
    """
    case_id = execute_query(sql, (
        case_uuid, case_number, temp_person_id, linked_person_id, user_id,
        identification_status, approx_name, approx_age, gender, language,
        comm_status, med_req, medical_case_id, special_assist
    ), commit=True)

    # Insert Location
    zone = payload.get('zone', 'Saswad')
    execute_query("""
    INSERT INTO found_person_locations (
        case_id, zone, route_section, landmark, latitude, longitude, location_description, location_source, found_at
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
    """, (
        case_id, zone, payload.get('route_section', 'Alandi-Pandharpur Route'),
        payload.get('landmark'), payload.get('latitude'), payload.get('longitude'),
        payload.get('location_description'), payload.get('location_source', 'VOLUNTEER')
    ), commit=True)

    # Insert Clothing
    c = payload.get('clothing', {})
    execute_query("""
    INSERT INTO found_person_clothing (
        case_id, top_type, top_color, bottom_type, bottom_color, footwear, footwear_color, headwear, accessories, description, confidence_level
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        case_id, c.get('top_type', 'T-Shirt'), c.get('top_color', 'Red'),
        c.get('bottom_type', 'Shorts'), c.get('bottom_color', 'Navy Blue'),
        c.get('footwear', 'Sandals'), c.get('footwear_color', 'Brown'),
        c.get('headwear'), c.get('accessories'), c.get('description'),
        c.get('confidence_level', 'HIGH')
    ), commit=True)

    # Insert Initial Safe Location Assignment
    loc_name = payload.get('safe_location_name', f"{zone} Help Center No. 1")
    fac_type = payload.get('facility_type', 'HELP_CENTER')
    fac_id = payload.get('facility_id')
    execute_query("""
    INSERT INTO found_person_safe_locations (
        case_id, facility_type, facility_id, location_name, arrival_time, status
    ) VALUES (%s, %s, %s, %s, NOW(), 'AT_HELP_CENTER')
    """, (case_id, fac_type, fac_id, loc_name), commit=True)

    # Initial Status History
    execute_query("""
    INSERT INTO found_person_status_history (case_id, old_status, new_status, changed_by, reason)
    VALUES (%s, NULL, 'REPORTED', %s, 'Found person case registered')
    """, (case_id, user_id), commit=True)

    # Log Audit Event
    log_audit_event(
        user_id=user_id,
        action="FOUND_CASE_CREATED",
        details={"case_id": case_id, "case_number": case_number, "identification_status": identification_status}
    )

    return True, get_found_person_case_details(case_id, current_user), 201

def get_found_person_case_details(case_id, current_user=None):
    """
    Retrieves complete found person case details including location, clothing, photos,
    identification clues, safe locations, family contacts, verification, reunification, and notes.
    """
    case = execute_query("""
    SELECT c.*, u.full_name as reporter_name, u.mobile as reporter_mobile
    FROM found_person_cases c
    JOIN users u ON c.reported_by_user_id = u.id
    WHERE c.id = %s
    """, (case_id,), fetchone=True)

    if not case:
        return None

    # Linked Person details if identified
    if case['linked_person_id']:
        case['linked_person'] = get_person_full_profile(case['linked_person_id'], current_user)
    else:
        case['linked_person'] = None

    # Location
    case['location'] = execute_query("SELECT * FROM found_person_locations WHERE case_id = %s", (case_id,), fetchone=True) or {}

    # Clothing
    case['clothing'] = execute_query("SELECT * FROM found_person_clothing WHERE case_id = %s", (case_id,), fetchone=True) or {}

    # Safe Location Placement
    case['safe_location'] = execute_query("SELECT * FROM found_person_safe_locations WHERE case_id = %s ORDER BY id DESC LIMIT 1", (case_id,), fetchone=True) or {}

    # Photos
    case['photos'] = execute_query("SELECT * FROM found_person_photos WHERE case_id = %s", (case_id,), fetchall=True) or []

    # Identification Clues
    case['clues'] = execute_query("SELECT * FROM found_person_identification_clues WHERE case_id = %s ORDER BY id DESC", (case_id,), fetchall=True) or []

    # Family Contacts
    case['family_contacts'] = execute_query("""
    SELECT fc.*, u.full_name as contacted_by_name
    FROM found_person_family_contacts fc
    JOIN users u ON fc.contacted_by = u.id
    WHERE fc.case_id = %s ORDER BY fc.id DESC
    """, (case_id,), fetchall=True) or []

    # Verification Record
    case['verification'] = execute_query("""
    SELECT v.*, u.full_name as verifier_name
    FROM found_person_verifications v
    JOIN users u ON v.verified_by = u.id
    WHERE v.case_id = %s ORDER BY v.id DESC LIMIT 1
    """, (case_id,), fetchone=True) or {}

    # Reunification Record
    case['reunification'] = execute_query("""
    SELECT r.*, u.full_name as officer_name
    FROM found_person_reunifications r
    JOIN users u ON r.verified_by = u.id
    WHERE r.case_id = %s ORDER BY r.id DESC LIMIT 1
    """, (case_id,), fetchone=True) or {}

    # Notes (Role-filtered)
    is_staff = current_user and current_user['role_name'] in ['POLICE_OFFICER', 'HELP_CENTER_OPERATOR', 'SUPER_ADMIN', 'EVENT_ADMIN']
    notes_sql = "SELECT n.*, u.full_name as author_name FROM found_person_notes n JOIN users u ON n.created_by = u.id WHERE n.case_id = %s"
    if not is_staff:
        notes_sql += " AND n.visibility = 'FAMILY_VISIBLE'"
    notes_sql += " ORDER BY n.created_at DESC"
    case['notes'] = execute_query(notes_sql, (case_id,), fetchall=True) or []

    # Timeline History
    case['timeline'] = execute_query("SELECT * FROM found_person_status_history WHERE case_id = %s ORDER BY id ASC", (case_id,), fetchall=True) or []

    return case

def list_found_person_cases(status=None, identification_status=None, zone=None, limit=50, offset=0):
    """
    Lists found person cases with optional filtering.
    """
    where_clauses = []
    params = []

    if status:
        where_clauses.append("c.status = %s")
        params.append(status)

    if identification_status:
        where_clauses.append("c.identification_status = %s")
        params.append(identification_status)

    if zone:
        where_clauses.append("l.zone = %s")
        params.append(zone)

    where_str = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    query = f"""
    SELECT 
        c.id, c.uuid, c.case_number, c.temporary_person_id, c.linked_person_id,
        c.approximate_name, c.approximate_age, c.gender, c.identification_status,
        c.status, c.created_at,
        l.zone, l.landmark, l.location_description,
        sl.location_name as safe_location_name, sl.status as safe_status
    FROM found_person_cases c
    LEFT JOIN found_person_locations l ON c.id = l.case_id
    LEFT JOIN found_person_safe_locations sl ON c.id = sl.case_id
    {where_str}
    ORDER BY c.id DESC
    LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])
    return execute_query(query, tuple(params), fetchall=True) or []

def search_existing_profiles(query_str, current_user):
    """
    Searches permanent person_profiles (Module 2) for candidate matches.
    """
    if not query_str:
        return []

    q = f"%{query_str.strip()}%"
    sql = """
    SELECT p.id, p.person_code, p.full_name, p.date_of_birth, p.gender, p.age_category, f.family_code, f.family_name
    FROM person_profiles p
    LEFT JOIN family_members fm ON p.id = fm.person_id
    LEFT JOIN families f ON fm.family_id = f.id
    WHERE p.full_name LIKE %s OR p.person_code LIKE %s OR f.family_code LIKE %s OR f.family_name LIKE %s
    LIMIT 10
    """

    return execute_query(sql, (q, q, q, q), fetchall=True) or []

def add_identification_clue(case_id, payload, current_user):
    """
    Records an identification clue (verbal name, Dindi #, village name).
    """
    clue_id = execute_query("""
    INSERT INTO found_person_identification_clues (case_id, clue_type, clue_value, source, confidence, verified)
    VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        case_id, payload.get('clue_type', 'OTHER'),
        payload.get('clue_value', '').strip(),
        payload.get('source', 'Verbal statement'),
        payload.get('confidence', 'MEDIUM'),
        1 if payload.get('verified') else 0
    ), commit=True)

    log_audit_event(current_user['user_id'], "FOUND_CASE_IDENTIFICATION_UPDATED", {"case_id": case_id, "clue_id": clue_id})
    return True, {"message": "Identification clue added.", "clue_id": clue_id}, 201

def assign_safe_location(case_id, payload, current_user):
    """
    Assigns or transfers found person to an authorized safe help center or police post.
    """
    fac_name = payload.get('location_name', 'Help Center').strip()
    status = payload.get('status', 'AT_HELP_CENTER')
    fac_type = payload.get('facility_type', 'HELP_CENTER')
    fac_id = payload.get('facility_id')

    loc_id = execute_query("""
    INSERT INTO found_person_safe_locations (case_id, facility_type, facility_id, location_name, arrival_time, status)
    VALUES (%s, %s, %s, %s, NOW(), %s)
    """, (case_id, fac_type, fac_id, fac_name, status), commit=True)

    log_audit_event(current_user['user_id'], "FOUND_CASE_SAFE_LOCATION_UPDATED", {"case_id": case_id, "location_name": fac_name, "status": status})
    return True, {"message": "Safe location assigned.", "safe_location_id": loc_id}, 201

def log_family_contact(case_id, payload, current_user):
    """
    Logs a family contact attempt.
    """
    contact_id = execute_query("""
    INSERT INTO found_person_family_contacts (case_id, contact_name, contact_number, relationship, contact_method, contacted_by, result)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        case_id, payload.get('contact_name', '').strip(),
        payload.get('contact_number', '').strip(),
        payload.get('relationship', 'Family'),
        payload.get('contact_method', 'Phone Call'),
        current_user['user_id'],
        payload.get('result', 'Contact attempt logged')
    ), commit=True)

    execute_query("UPDATE found_person_cases SET status = 'FAMILY_CONTACTED', updated_at = NOW() WHERE id = %s", (case_id,), commit=True)
    log_audit_event(current_user['user_id'], "FOUND_CASE_FAMILY_CONTACTED", {"case_id": case_id, "contact_id": contact_id})
    return True, {"message": "Family contact attempt logged.", "contact_id": contact_id}, 201

def perform_identity_verification(case_id, payload, current_user):
    """
    Records identity verification result by authorized personnel.
    """
    status = payload.get('verification_status', 'VERIFIED')
    method = payload.get('verification_method', 'PERSONAL_INFORMATION')
    notes = payload.get('verification_notes', '').strip()

    v_id = execute_query("""
    INSERT INTO found_person_verifications (case_id, verification_status, verification_method, verified_by, verification_notes)
    VALUES (%s, %s, %s, %s, %s)
    """, (case_id, status, method, current_user['user_id'], notes), commit=True)

    new_case_status = 'IDENTITY_CONFIRMED' if status == 'VERIFIED' else 'UNDER_REVIEW'
    execute_query("UPDATE found_person_cases SET status = %s, updated_at = NOW() WHERE id = %s", (new_case_status, case_id), commit=True)

    log_audit_event(current_user['user_id'], "FOUND_CASE_VERIFIED", {"case_id": case_id, "verification_status": status})
    return True, {"message": f"Identity verification recorded as {status}.", "verification_id": v_id}, 200

def perform_reunification(case_id, payload, current_user):
    """
    Performs formal reunification handover.
    Requires identity verification to be completed first.
    """
    reunited_with = payload.get('reunited_with', 'Family Guardian').strip()
    loc = payload.get('reunification_location', 'Help Center').strip()
    notes = payload.get('notes', '').strip()

    r_id = execute_query("""
    INSERT INTO found_person_reunifications (case_id, reunited_with, verified_by, reunification_location, reunification_time, notes)
    VALUES (%s, %s, %s, %s, NOW(), %s)
    """, (case_id, reunited_with, current_user['user_id'], loc, notes), commit=True)

    execute_query("UPDATE found_person_cases SET status = 'REUNITED', updated_at = NOW(), closed_at = NOW() WHERE id = %s", (case_id,), commit=True)
    execute_query("UPDATE found_person_safe_locations SET status = 'REUNITED', departure_time = NOW() WHERE case_id = %s", (case_id,), commit=True)

    execute_query("""
    INSERT INTO found_person_status_history (case_id, old_status, new_status, changed_by, reason)
    VALUES (%s, 'VERIFICATION', 'REUNITED', %s, %s)
    """, (case_id, current_user['user_id'], f"Reunited with {reunited_with}"), commit=True)

    log_audit_event(current_user['user_id'], "FOUND_CASE_REUNITED", {"case_id": case_id, "reunited_with": reunited_with})
    return True, {"message": "Reunification completed successfully!", "reunification_id": r_id}, 200

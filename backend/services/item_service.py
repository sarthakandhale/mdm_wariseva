import uuid
from datetime import datetime
from db import execute_query
from services.audit_service import log_audit_event

def generate_lost_item_code():
    """Generates unique Lost Item Case Code: WS-LI-2026-XXXXXX"""
    res = execute_query("SELECT COUNT(*) as cnt FROM lost_item_cases", fetchone=True)
    next_num = (res['cnt'] if res else 0) + 1
    return f"WS-LI-2026-{next_num:06d}"

def generate_found_item_code():
    """Generates unique Found Item Case Code: WS-FI-2026-XXXXXX"""
    res = execute_query("SELECT COUNT(*) as cnt FROM found_item_cases", fetchone=True)
    next_num = (res['cnt'] if res else 0) + 1
    return f"WS-FI-2026-{next_num:06d}"

def generate_claim_code():
    """Generates unique Claim Number: CLM-2026-XXXXXX"""
    res = execute_query("SELECT COUNT(*) as cnt FROM item_claims", fetchone=True)
    next_num = (res['cnt'] if res else 0) + 1
    return f"CLM-2026-{next_num:06d}"

def mask_sensitive_value(val):
    """Masks sensitive numbers (e.g. IMEI/Serial Number) showing only last 4 digits"""
    if not val:
        return None
    s = str(val).strip()
    if len(s) <= 4:
        return "****"
    return "*" * (len(s) - 4) + s[-4:]

def create_lost_item_case(payload, current_user):
    """
    Files a new lost item case with location, sensitive identifier storage, and audit logging.
    """
    user_id = current_user['user_id']
    case_number = generate_lost_item_code()
    case_uuid = f"li-{uuid.uuid4().hex[:12]}"

    category = payload.get('item_category', 'OTHER')
    name = payload.get('item_name', 'Lost Belonging').strip()
    brand = payload.get('brand', '').strip()
    model = payload.get('model', '').strip()
    color = payload.get('color', '').strip()
    desc = payload.get('description', '').strip()
    val = float(payload.get('approximate_value', 0.0))
    serial_no = payload.get('serial_number', '').strip() or None
    imei = payload.get('imei', '').strip() or None

    sql = """
    INSERT INTO lost_item_cases (
        uuid, case_number, reported_by_user_id, item_category, item_name,
        brand, model, color, description, approximate_value, serial_number, imei, status
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'REPORTED')
    """
    case_id = execute_query(sql, (
        case_uuid, case_number, user_id, category, name,
        brand, model, color, desc, val, serial_no, imei
    ), commit=True)

    # Insert Location
    zone = payload.get('zone', 'Saswad')
    execute_query("""
    INSERT INTO item_locations (
        lost_item_case_id, zone, route_section, landmark, latitude, longitude, location_type, location_description
    ) VALUES (%s, %s, %s, %s, %s, %s, 'LOST', %s)
    """, (
        case_id, zone, payload.get('route_section', 'Alandi-Pandharpur Route'),
        payload.get('landmark'), payload.get('latitude'), payload.get('longitude'),
        payload.get('location_description')
    ), commit=True)

    # Insert Restricted Identifiers if provided
    if serial_no:
        execute_query("""
        INSERT INTO item_identifiers (lost_item_case_id, identifier_type, identifier_value, visibility)
        VALUES (%s, 'SERIAL_NUMBER', %s, 'AUTHORIZED_ONLY')
        """, (case_id, serial_no), commit=True)

    if imei:
        execute_query("""
        INSERT INTO item_identifiers (lost_item_case_id, identifier_type, identifier_value, visibility)
        VALUES (%s, 'IMEI', %s, 'AUTHORIZED_ONLY')
        """, (case_id, imei), commit=True)

    # Initial Status History
    execute_query("""
    INSERT INTO item_status_history (lost_item_case_id, old_status, new_status, changed_by, reason)
    VALUES (%s, NULL, 'REPORTED', %s, 'Lost item report created')
    """, (case_id, user_id), commit=True)

    log_audit_event(user_id, "LOST_ITEM_CREATED", {"case_id": case_id, "case_number": case_number, "category": category})
    return True, get_lost_item_details(case_id, current_user), 201

def create_found_item_case(payload, current_user):
    """
    Registers a found physical item with location, storage assignment, chain of custody, and audit log.
    """
    user_id = current_user['user_id']
    case_number = generate_found_item_code()
    case_uuid = f"fi-{uuid.uuid4().hex[:12]}"

    category = payload.get('item_category', 'OTHER')
    name = payload.get('item_name', 'Found Belonging').strip()
    brand = payload.get('brand', '').strip()
    model = payload.get('model', '').strip()
    color = payload.get('color', '').strip()
    desc = payload.get('description', '').strip()
    condition = payload.get('condition', 'GOOD')

    sql = """
    INSERT INTO found_item_cases (
        uuid, case_number, reported_by_user_id, item_category, item_name,
        brand, model, color, description, `condition`, found_by_user_id, status
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'STORED')
    """
    case_id = execute_query(sql, (
        case_uuid, case_number, user_id, category, name,
        brand, model, color, desc, condition, user_id
    ), commit=True)

    # Insert Location
    zone = payload.get('zone', 'Saswad')
    execute_query("""
    INSERT INTO item_locations (
        found_item_case_id, zone, route_section, landmark, latitude, longitude, location_type, location_description
    ) VALUES (%s, %s, %s, %s, %s, %s, 'FOUND', %s)
    """, (
        case_id, zone, payload.get('route_section', 'Alandi-Pandharpur Route'),
        payload.get('landmark'), payload.get('latitude'), payload.get('longitude'),
        payload.get('location_description')
    ), commit=True)

    # Initial Storage & Custody Assignment
    fac_name = payload.get('facility_name', f"{zone} Help Center Storage Tent 2")
    execute_query("""
    INSERT INTO item_custody_history (found_item_case_id, from_user_id, to_user_id, from_location, to_location, action, notes)
    VALUES (%s, %s, %s, %s, %s, 'STORED', 'Initial storage receipt')
    """, (case_id, user_id, user_id, payload.get('landmark', 'Found Location'), fac_name), commit=True)

    # Initial Status History
    execute_query("""
    INSERT INTO item_status_history (found_item_case_id, old_status, new_status, changed_by, reason)
    VALUES (%s, NULL, 'STORED', %s, 'Found item registered & stored')
    """, (case_id, user_id), commit=True)

    log_audit_event(user_id, "FOUND_ITEM_CREATED", {"case_id": case_id, "case_number": case_number, "category": category})
    return True, get_found_item_details(case_id, current_user), 201

def get_lost_item_details(case_id, current_user=None):
    """
    Retrieves lost item details with privacy masking on serial numbers and IMEIs for unprivileged users.
    """
    case = execute_query("""
    SELECT c.*, u.full_name as reporter_name, u.mobile as reporter_mobile
    FROM lost_item_cases c
    JOIN users u ON c.reported_by_user_id = u.id
    WHERE c.id = %s
    """, (case_id,), fetchone=True)

    if not case:
        return None

    is_owner_or_staff = current_user and (
        current_user['user_id'] == case['reported_by_user_id'] or
        current_user['role_name'] in ['POLICE_OFFICER', 'HELP_CENTER_OPERATOR', 'SUPER_ADMIN', 'EVENT_ADMIN']
    )

    if not is_owner_or_staff:
        case['serial_number'] = mask_sensitive_value(case['serial_number'])
        case['imei'] = mask_sensitive_value(case['imei'])

    case['location'] = execute_query("SELECT * FROM item_locations WHERE lost_item_case_id = %s", (case_id,), fetchone=True) or {}
    case['photos'] = execute_query("SELECT * FROM item_photos WHERE lost_item_case_id = %s", (case_id,), fetchall=True) or []
    case['timeline'] = execute_query("SELECT * FROM item_status_history WHERE lost_item_case_id = %s ORDER BY id ASC", (case_id,), fetchall=True) or []
    return case

def get_found_item_details(case_id, current_user=None):
    """
    Retrieves found item details, custody chain, claims, and notes.
    """
    case = execute_query("""
    SELECT c.*, u.full_name as reporter_name, u.mobile as reporter_mobile
    FROM found_item_cases c
    JOIN users u ON c.reported_by_user_id = u.id
    WHERE c.id = %s
    """, (case_id,), fetchone=True)

    if not case:
        return None

    case['location'] = execute_query("SELECT * FROM item_locations WHERE found_item_case_id = %s", (case_id,), fetchone=True) or {}
    case['photos'] = execute_query("SELECT * FROM item_photos WHERE found_item_case_id = %s", (case_id,), fetchall=True) or []
    case['custody_chain'] = execute_query("""
    SELECT ch.*, u1.full_name as from_user_name, u2.full_name as to_user_name
    FROM item_custody_history ch
    LEFT JOIN users u1 ON ch.from_user_id = u1.id
    JOIN users u2 ON ch.to_user_id = u2.id
    WHERE ch.found_item_case_id = %s ORDER BY ch.id ASC
    """, (case_id,), fetchall=True) or []

    case['claims'] = execute_query("""
    SELECT ic.*, u.full_name as claimant_name, u.mobile as claimant_mobile
    FROM item_claims ic
    JOIN users u ON ic.claimed_by_user_id = u.id
    WHERE ic.found_item_case_id = %s ORDER BY ic.id DESC
    """, (case_id,), fetchall=True) or []

    case['timeline'] = execute_query("SELECT * FROM item_status_history WHERE found_item_case_id = %s ORDER BY id ASC", (case_id,), fetchall=True) or []
    return case

def list_lost_items(category=None, zone=None, status=None, limit=50, offset=0):
    """Lists lost items with optional filtering"""
    where_clauses = []
    params = []
    if category:
        where_clauses.append("c.item_category = %s")
        params.append(category)
    if status:
        where_clauses.append("c.status = %s")
        params.append(status)
    if zone:
        where_clauses.append("l.zone = %s")
        params.append(zone)

    where_str = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    query = f"""
    SELECT c.id, c.case_number, c.item_category, c.item_name, c.brand, c.color, c.status, c.created_at, l.zone, l.landmark
    FROM lost_item_cases c
    LEFT JOIN item_locations l ON c.id = l.lost_item_case_id
    {where_str}
    ORDER BY c.id DESC LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])
    return execute_query(query, tuple(params), fetchall=True) or []

def list_found_items(category=None, zone=None, status=None, limit=50, offset=0):
    """Lists found items with optional filtering"""
    where_clauses = []
    params = []
    if category:
        where_clauses.append("c.item_category = %s")
        params.append(category)
    if status:
        where_clauses.append("c.status = %s")
        params.append(status)
    if zone:
        where_clauses.append("l.zone = %s")
        params.append(zone)

    where_str = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    query = f"""
    SELECT c.id, c.case_number, c.item_category, c.item_name, c.brand, c.color, c.condition, c.status, c.created_at, l.zone, l.landmark
    FROM found_item_cases c
    LEFT JOIN item_locations l ON c.id = l.found_item_case_id
    {where_str}
    ORDER BY c.id DESC LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])
    return execute_query(query, tuple(params), fetchall=True) or []

def submit_item_claim(found_case_id, payload, current_user):
    """
    Submits an owner claim for a found physical item.
    """
    user_id = current_user['user_id']
    claim_number = generate_claim_code()
    desc = payload.get('claim_description', '').strip()

    claim_id = execute_query("""
    INSERT INTO item_claims (claim_number, found_item_case_id, claimed_by_user_id, claim_description, status)
    VALUES (%s, %s, %s, %s, 'SUBMITTED')
    """, (claim_number, found_case_id, user_id, desc), commit=True)

    execute_query("UPDATE found_item_cases SET status = 'CLAIM_PENDING', updated_at = NOW() WHERE id = %s", (found_case_id,), commit=True)
    log_audit_event(user_id, "CLAIM_CREATED", {"found_case_id": found_case_id, "claim_number": claim_number})
    return True, {"message": "Item claim submitted.", "claim_number": claim_number, "claim_id": claim_id}, 201

def verify_claim(claim_id, payload, current_user):
    """
    Verifies and approves/rejects an owner claim.
    When APPROVED, competing active claims for the same found item update to REJECTED.
    """
    status = payload.get('status', 'APPROVED') # APPROVED or REJECTED
    notes = payload.get('notes', '').strip()

    claim = execute_query("SELECT found_item_case_id FROM item_claims WHERE id = %s", (claim_id,), fetchone=True)
    if not claim:
        return False, {"message": "Claim not found.", "error_code": "NOT_FOUND"}, 404

    found_case_id = claim['found_item_case_id']

    execute_query("""
    UPDATE item_claims
    SET status = %s, reviewed_by = %s, reviewed_at = NOW()
    WHERE id = %s
    """, (status, current_user['user_id'], claim_id), commit=True)

    execute_query("""
    INSERT INTO item_claim_verifications (claim_id, verification_type, verification_result, verification_notes, verified_by)
    VALUES (%s, 'DESCRIPTION', %s, %s, %s)
    """, (claim_id, 'MATCH' if status == 'APPROVED' else 'NO_MATCH', notes, current_user['user_id']), commit=True)

    if status == 'APPROVED':
        execute_query("UPDATE found_item_cases SET status = 'VERIFICATION', updated_at = NOW() WHERE id = %s", (found_case_id,), commit=True)
        # Reject competing active claims
        execute_query("UPDATE item_claims SET status = 'REJECTED' WHERE found_item_case_id = %s AND id != %s AND status = 'SUBMITTED'", (found_case_id, claim_id), commit=True)
        log_audit_event(current_user['user_id'], "CLAIM_APPROVED", {"claim_id": claim_id, "found_case_id": found_case_id})
    else:
        log_audit_event(current_user['user_id'], "CLAIM_REJECTED", {"claim_id": claim_id, "found_case_id": found_case_id})

    return True, {"message": f"Claim status updated to {status}."}, 200

def manual_match_items(lost_case_id, found_case_id, reason, current_user):
    """
    Pairs Lost Item ↔ Found Item manually.
    """
    match_id = execute_query("""
    INSERT INTO item_matches (lost_item_case_id, found_item_case_id, match_type, match_score, match_reason, created_by, status)
    VALUES (%s, %s, 'MANUAL', 100, %s, %s, 'MANUAL_POTENTIAL_MATCH')
    """, (lost_case_id, found_case_id, reason, current_user['user_id']), commit=True)

    execute_query("UPDATE lost_item_cases SET status = 'POTENTIAL_MATCH', updated_at = NOW() WHERE id = %s", (lost_case_id,), commit=True)
    execute_query("UPDATE found_item_cases SET status = 'POTENTIAL_MATCH', updated_at = NOW() WHERE id = %s", (found_case_id,), commit=True)

    log_audit_event(current_user['user_id'], "ITEM_MATCH_CREATED", {"lost_case_id": lost_case_id, "found_case_id": found_case_id})
    return True, {"message": "Manual item potential match created.", "match_id": match_id}, 201

def release_found_item(found_case_id, payload, current_user):
    """
    Performs formal return handover of physical found item to verified owner.
    """
    returned_to = payload.get('returned_to', 'Verified Owner').strip()
    loc = payload.get('return_location', 'Help Center').strip()
    notes = payload.get('notes', '').strip()

    execute_query("UPDATE found_item_cases SET status = 'RETURNED', updated_at = NOW(), closed_at = NOW() WHERE id = %s", (found_case_id,), commit=True)
    
    execute_query("""
    INSERT INTO item_custody_history (found_item_case_id, from_user_id, to_user_id, from_location, to_location, action, notes)
    VALUES (%s, %s, %s, %s, %s, 'RELEASED', %s)
    """, (found_case_id, current_user['user_id'], current_user['user_id'], loc, returned_to, f"Released to {returned_to}: {notes}"), commit=True)

    execute_query("""
    INSERT INTO item_status_history (found_item_case_id, old_status, new_status, changed_by, reason)
    VALUES (%s, 'VERIFICATION', 'RETURNED', %s, %s)
    """, (found_case_id, current_user['user_id'], f"Item returned to {returned_to}"), commit=True)

    log_audit_event(current_user['user_id'], "ITEM_RELEASED", {"found_case_id": found_case_id, "returned_to": returned_to})
    return True, {"message": "Found item returned to verified owner successfully!"}, 200

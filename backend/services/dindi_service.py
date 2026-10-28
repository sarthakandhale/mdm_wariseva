import uuid
from datetime import datetime
from db import execute_query
from services.audit_service import log_audit_event

def generate_dindi_code(dindi_number):
    """Generates unique Dindi Code: WS-DIN-2026-XXXXXX"""
    return f"WS-DIN-2026-{int(dindi_number):06d}"

def create_dindi(payload, current_user):
    """
    Registers a new Dindi group with leader, contacts, and verification record.
    Prevents duplicate Dindi number.
    """
    user_id = current_user['user_id']
    dindi_num = int(payload.get('dindi_number', 0))

    if dindi_num <= 0:
        return False, {"message": "Invalid Dindi number.", "error_code": "INVALID_NUMBER"}, 400

    existing = execute_query("SELECT id FROM dindis WHERE dindi_number = %s", (dindi_num,), fetchone=True)
    if existing:
        return False, {"message": f"Dindi number {dindi_num} is already registered.", "error_code": "DUPLICATE_NUMBER"}, 400

    dindi_code = generate_dindi_code(dindi_num)
    dindi_uuid = f"din-{uuid.uuid4().hex[:12]}"

    name = payload.get('name', f"Dindi No. {dindi_num}").strip()
    desc = payload.get('description', '').strip()
    start_loc = payload.get('start_location', 'Alandi').strip()
    dest = payload.get('destination', 'Pandharpur').strip()
    expected_count = int(payload.get('expected_member_count', 100))

    sql = """
    INSERT INTO dindis (
        uuid, dindi_code, dindi_number, name, description, registration_year,
        start_location, destination, expected_member_count, status, created_by
    ) VALUES (%s, %s, %s, %s, %s, 2026, %s, %s, %s, 'PENDING', %s)
    """
    dindi_id = execute_query(sql, (
        dindi_uuid, dindi_code, dindi_num, name, desc, start_loc, dest, expected_count, user_id
    ), commit=True)

    # Insert Leader if provided
    leader_user_id = payload.get('leader_user_id', user_id)
    execute_query("""
    INSERT INTO dindi_leaders (dindi_id, user_id, role, status)
    VALUES (%s, %s, 'PRIMARY_LEADER', 'ACTIVE')
    """, (dindi_id, leader_user_id), commit=True)

    # Insert Primary Contact
    contact_name = payload.get('contact_name', current_user.get('full_name', 'Leader'))
    contact_num = payload.get('contact_number', current_user.get('mobile', ''))
    execute_query("""
    INSERT INTO dindi_contacts (dindi_id, contact_type, contact_name, contact_number, visibility)
    VALUES (%s, 'PRIMARY', %s, %s, 'PUBLIC')
    """, (dindi_id, contact_name, contact_num), commit=True)

    # Initial Verification Record
    execute_query("""
    INSERT INTO dindi_verifications (dindi_id, status, verified_by, verification_notes)
    VALUES (%s, 'PENDING', %s, 'Pending administrative verification')
    """, (dindi_id, user_id), commit=True)

    log_audit_event(user_id, "DINDI_CREATED", {"dindi_id": dindi_id, "dindi_code": dindi_code, "dindi_number": dindi_num})
    return True, get_dindi_details(dindi_id), 201

def get_dindi_details(dindi_id):
    """
    Retrieves full details of a Dindi, including leaders, member count, schedules, announcements, contacts.
    """
    dindi = execute_query("SELECT * FROM dindis WHERE id = %s", (dindi_id,), fetchone=True)
    if not dindi:
        return None

    # Leaders
    dindi['leaders'] = execute_query("""
    SELECT dl.*, u.full_name, u.mobile, u.email
    FROM dindi_leaders dl
    JOIN users u ON dl.user_id = u.id
    WHERE dl.dindi_id = %s AND dl.status = 'ACTIVE'
    """, (dindi_id,), fetchall=True) or []

    # Member Count Breakdown
    cnt_res = execute_query("""
    SELECT COUNT(*) as total_members,
           SUM(CASE WHEN status = 'ACTIVE' THEN 1 ELSE 0 END) as active_members,
           SUM(CASE WHEN role = 'VOLUNTEER' THEN 1 ELSE 0 END) as volunteer_count
    FROM dindi_memberships WHERE dindi_id = %s
    """, (dindi_id,), fetchone=True) or {}

    dindi['member_stats'] = {
        "registered_members": cnt_res.get('total_members', 0),
        "active_members": cnt_res.get('active_members', 0),
        "volunteers": cnt_res.get('volunteer_count', 0)
    }

    # Schedules
    dindi['schedules'] = execute_query("""
    SELECT * FROM dindi_schedules WHERE dindi_id = %s ORDER BY schedule_date ASC
    """, (dindi_id,), fetchall=True) or []

    # Announcements
    dindi['announcements'] = execute_query("""
    SELECT da.*, u.full_name as author_name
    FROM dindi_announcements da
    JOIN users u ON da.created_by = u.id
    WHERE da.dindi_id = %s AND da.status = 'ACTIVE'
    ORDER BY da.id DESC
    """, (dindi_id,), fetchall=True) or []

    # Contacts
    dindi['contacts'] = execute_query("SELECT * FROM dindi_contacts WHERE dindi_id = %s", (dindi_id,), fetchall=True) or []
    return dindi

def list_dindis(number=None, name=None, status=None, limit=50, offset=0):
    """Lists Dindis with optional filtering"""
    where_clauses = []
    params = []
    if number:
        where_clauses.append("dindi_number = %s")
        params.append(number)
    if status:
        where_clauses.append("status = %s")
        params.append(status)
    if name:
        where_clauses.append("name LIKE %s")
        params.append(f"%{name}%")

    where_str = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    query = f"""
    SELECT d.id, d.dindi_code, d.dindi_number, d.name, d.start_location, d.destination, d.expected_member_count, d.status, d.created_at,
           (SELECT COUNT(*) FROM dindi_memberships m WHERE m.dindi_id = d.id AND m.status = 'ACTIVE') as active_member_count
    FROM dindis d
    {where_str}
    ORDER BY d.dindi_number ASC LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])
    return execute_query(query, tuple(params), fetchall=True) or []

def add_dindi_member(dindi_id, person_id, role, current_user):
    """
    Enrolls a person profile into a Dindi membership.
    Prevents duplicate membership.
    """
    existing = execute_query("""
    SELECT id FROM dindi_memberships WHERE dindi_id = %s AND person_id = %s
    """, (dindi_id, person_id), fetchone=True)
    if existing:
        return False, {"message": "Person is already a member of this Dindi.", "error_code": "DUPLICATE_MEMBER"}, 400

    dindi = execute_query("SELECT dindi_number FROM dindis WHERE id = %s", (dindi_id,), fetchone=True)
    if not dindi:
        return False, {"message": "Dindi not found.", "error_code": "NOT_FOUND"}, 404

    mem_num = f"MEM-DIN{dindi['dindi_number']}-{person_id:04d}"

    mem_id = execute_query("""
    INSERT INTO dindi_memberships (dindi_id, person_id, membership_number, role, status)
    VALUES (%s, %s, %s, %s, 'ACTIVE')
    """, (dindi_id, person_id, mem_num, role or 'MEMBER'), commit=True)

    log_audit_event(current_user['user_id'], "DINDI_MEMBER_ADDED", {"dindi_id": dindi_id, "person_id": person_id, "role": role})
    return True, {"message": "Member enrolled into Dindi.", "membership_id": mem_id, "membership_number": mem_num}, 201

def list_dindi_members(dindi_id):
    """Lists enrolled members of a Dindi with person profile details"""
    query = """
    SELECT dm.*, p.first_name, p.last_name, p.calculated_age, p.gender, p.person_code, p.primary_mobile
    FROM dindi_memberships dm
    JOIN person_profiles p ON dm.person_id = p.id
    WHERE dm.dindi_id = %s
    ORDER BY dm.id ASC
    """
    return execute_query(query, (dindi_id,), fetchall=True) or []

def assign_dindi_leader(dindi_id, target_user_id, role, current_user):
    """
    Assigns a user as Primary Leader or Assistant Leader of a Dindi.
    """
    leader_id = execute_query("""
    INSERT INTO dindi_leaders (dindi_id, user_id, role, status)
    VALUES (%s, %s, %s, 'ACTIVE')
    """, (dindi_id, target_user_id, role or 'ASSISTANT_LEADER'), commit=True)

    log_audit_event(current_user['user_id'], "DINDI_LEADER_ASSIGNED", {"dindi_id": dindi_id, "target_user_id": target_user_id, "role": role})
    return True, {"message": f"User assigned as {role} for Dindi.", "leader_id": leader_id}, 201

def create_dindi_schedule(dindi_id, payload, current_user):
    """Publishes a daily march & rest schedule item for a Dindi"""
    dt = payload.get('schedule_date', datetime.now().strftime('%Y-%m-%d'))
    start_loc = payload.get('start_location', 'Alandi').strip()
    end_loc = payload.get('end_location', 'Pune').strip()
    start_time = payload.get('expected_start_time', '05:30 AM').strip()
    arr_time = payload.get('expected_arrival_time', '06:00 PM').strip()
    rest_point = payload.get('rest_point', '').strip()
    notes = payload.get('notes', '').strip()

    sch_id = execute_query("""
    INSERT INTO dindi_schedules (
        dindi_id, schedule_date, start_location, end_location,
        expected_start_time, expected_arrival_time, rest_point, notes, status
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'SCHEDULED')
    """, (dindi_id, dt, start_loc, end_loc, start_time, arr_time, rest_point, notes), commit=True)

    log_audit_event(current_user['user_id'], "DINDI_SCHEDULE_CREATED", {"dindi_id": dindi_id, "schedule_id": sch_id})
    return True, {"message": "Dindi schedule item created.", "schedule_id": sch_id}, 201

def create_dindi_announcement(dindi_id, payload, current_user):
    """Publishes an announcement to Dindi members"""
    title = payload.get('title', 'Dindi Update').strip()
    msg = payload.get('message', '').strip()
    priority = payload.get('priority', 'NORMAL')

    ann_id = execute_query("""
    INSERT INTO dindi_announcements (dindi_id, title, message, priority, created_by, status)
    VALUES (%s, %s, %s, %s, %s, 'ACTIVE')
    """, (dindi_id, title, msg, priority, current_user['user_id']), commit=True)

    log_audit_event(current_user['user_id'], "DINDI_ANNOUNCEMENT_CREATED", {"dindi_id": dindi_id, "announcement_id": ann_id, "priority": priority})
    return True, {"message": "Dindi announcement published.", "announcement_id": ann_id}, 201

def verify_dindi(dindi_id, payload, current_user):
    """Verifies Dindi group status (`VERIFIED`, `REJECTED`, `REQUIRES_UPDATE`)"""
    status = payload.get('status', 'VERIFIED')
    notes = payload.get('verification_notes', '').strip()

    execute_query("UPDATE dindis SET status = %s, updated_at = NOW() WHERE id = %s", (status, dindi_id), commit=True)

    execute_query("""
    INSERT INTO dindi_verifications (dindi_id, status, verified_by, verification_notes)
    VALUES (%s, %s, %s, %s)
    """, (dindi_id, status, current_user['user_id'], notes), commit=True)

    log_audit_event(current_user['user_id'], "DINDI_VERIFIED", {"dindi_id": dindi_id, "status": status})
    return True, {"message": f"Dindi verification status set to {status}."}, 200

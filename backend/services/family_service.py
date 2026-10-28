import uuid
from db import execute_query
from utils.validators import validate_mobile
from services.audit_service import log_audit_event
from services.person_service import get_person_full_profile

def generate_family_code():
    """Generates unique Family ID code: RY-FAM-2026-XXXXXX"""
    res = execute_query("SELECT COUNT(*) as cnt FROM families", fetchone=True)
    next_num = (res['cnt'] if res else 0) + 1
    return f"RY-FAM-2026-{next_num:06d}"

def create_family(payload, current_user):
    """
    Creates a new family group associated with the authenticated user.
    """
    user_id = current_user['user_id']
    family_name = payload.get('family_name', '').strip()
    primary_name = payload.get('primary_contact_name', '').strip() or current_user['full_name']
    primary_mobile = payload.get('primary_contact_mobile', '').strip() or current_user['mobile']
    emergency_name = payload.get('emergency_contact_name', '').strip()
    emergency_mobile = payload.get('emergency_contact_mobile', '').strip()
    preferred_lang = payload.get('preferred_language', 'en')
    notes = payload.get('notes', '')

    # Validations
    if not family_name or len(family_name) < 2 or len(family_name) > 100:
        return False, {"message": "Family Name is required and must be between 2 and 100 characters.", "error_code": "INVALID_FAMILY_NAME"}, 400

    if not primary_name:
        return False, {"message": "Primary Contact Name is required.", "error_code": "INVALID_PRIMARY_CONTACT"}, 400

    valid_mob, mob_res = validate_mobile(primary_mobile)
    if not valid_mob:
        return False, {"message": mob_res, "error_code": "INVALID_MOBILE"}, 400
    clean_primary_mob = mob_res

    if not emergency_name:
        return False, {"message": "Emergency Contact Name is required.", "error_code": "INVALID_EMERGENCY_CONTACT"}, 400

    valid_em_mob, em_mob_res = validate_mobile(emergency_mobile)
    if not valid_em_mob:
        return False, {"message": em_mob_res, "error_code": "INVALID_EMERGENCY_MOBILE"}, 400
    clean_em_mob = em_mob_res

    family_code = generate_family_code()
    fam_uuid = f"fam-{uuid.uuid4().hex[:12]}"

    sql = """
    INSERT INTO families (
        uuid, family_code, family_name, owner_user_id, primary_contact_name,
        primary_contact_mobile, emergency_contact_name, emergency_contact_mobile,
        preferred_language, notes, status
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'ACTIVE')
    """
    family_id = execute_query(sql, (
        fam_uuid, family_code, family_name, user_id, primary_name,
        clean_primary_mob, emergency_name, clean_em_mob,
        preferred_lang, notes
    ), commit=True)

    # Insert Family Access Owner Mapping
    execute_query("""
    INSERT INTO family_access (family_id, user_id, access_level, status)
    VALUES (%s, %s, 'OWNER', 'ACTIVE')
    """, (family_id, user_id), commit=True)

    # Log Audit Event
    log_audit_event(
        user_id=user_id,
        action="FAMILY_CREATED",
        details={"family_id": family_id, "family_code": family_code, "family_name": family_name}
    )

    return True, get_family_by_id(family_id, current_user), 201

def get_family_by_id(family_id, current_user=None):
    """
    Retrieves family summary details and active members.
    """
    family = execute_query("SELECT * FROM families WHERE id = %s AND status = 'ACTIVE'", (family_id,), fetchone=True)
    if not family:
        return None

    # Fetch family members
    members_query = """
    SELECT 
        fm.id as member_id, fm.relationship_type, fm.status as member_status,
        p.id as person_id, p.uuid as person_uuid, p.person_code, p.full_name,
        p.date_of_birth, p.gender, p.age_category, p.status as person_status
    FROM family_members fm
    JOIN person_profiles p ON fm.person_id = p.id
    WHERE fm.family_id = %s AND fm.status = 'ACTIVE'
    ORDER BY p.id ASC
    """
    raw_members = execute_query(members_query, (family_id,), fetchall=True)

    members = []
    for m in raw_members:
        full_p = get_person_full_profile(m['person_id'], current_user)
        if full_p:
            full_p['relationship'] = m['relationship_type']
            members.append(full_p)

    family['members'] = members
    family['member_count'] = len(members)
    return family

def list_families_for_user(current_user):
    """
    Lists families owned by or accessible to the current user.
    """
    user_id = current_user['user_id']
    role_name = current_user['role_name']

    if role_name in ['SUPER_ADMIN', 'EVENT_ADMIN']:
        query = "SELECT * FROM families WHERE status = 'ACTIVE' ORDER BY id DESC"
        families = execute_query(query, fetchall=True)
    else:
        query = """
        SELECT DISTINCT f.* 
        FROM families f
        LEFT JOIN family_access fa ON f.id = fa.family_id
        WHERE (f.owner_user_id = %s OR (fa.user_id = %s AND fa.status = 'ACTIVE'))
        AND f.status = 'ACTIVE'
        ORDER BY f.id DESC
        """
        families = execute_query(query, (user_id, user_id), fetchall=True)

    result = []
    for f in families:
        fam_detail = get_family_by_id(f['id'], current_user)
        if fam_detail:
            result.append(fam_detail)
    return result

def update_family(family_id, payload, current_user):
    """
    Updates family metadata (family_name, contacts, notes).
    """
    family = execute_query("SELECT * FROM families WHERE id = %s AND status = 'ACTIVE'", (family_id,), fetchone=True)
    if not family:
        return False, {"message": "Family not found.", "error_code": "NOT_FOUND"}, 404

    updates = []
    params = []

    if 'family_name' in payload and payload['family_name'].strip():
        name = payload['family_name'].strip()
        if len(name) < 2 or len(name) > 100:
            return False, {"message": "Family Name must be between 2 and 100 characters.", "error_code": "INVALID_NAME"}, 400
        updates.append("family_name = %s")
        params.append(name)

    if 'primary_contact_name' in payload and payload['primary_contact_name'].strip():
        updates.append("primary_contact_name = %s")
        params.append(payload['primary_contact_name'].strip())

    if 'primary_contact_mobile' in payload and payload['primary_contact_mobile'].strip():
        valid_mob, mob_res = validate_mobile(payload['primary_contact_mobile'])
        if not valid_mob:
            return False, {"message": mob_res, "error_code": "INVALID_MOBILE"}, 400
        updates.append("primary_contact_mobile = %s")
        params.append(mob_res)

    if 'emergency_contact_name' in payload and payload['emergency_contact_name'].strip():
        updates.append("emergency_contact_name = %s")
        params.append(payload['emergency_contact_name'].strip())

    if 'emergency_contact_mobile' in payload and payload['emergency_contact_mobile'].strip():
        valid_em, em_res = validate_mobile(payload['emergency_contact_mobile'])
        if not valid_em:
            return False, {"message": em_res, "error_code": "INVALID_MOBILE"}, 400
        updates.append("emergency_contact_mobile = %s")
        params.append(em_res)

    if 'preferred_language' in payload:
        updates.append("preferred_language = %s")
        params.append(payload['preferred_language'])

    if 'notes' in payload:
        updates.append("notes = %s")
        params.append(payload['notes'])

    if updates:
        updates.append("updated_at = NOW()")
        sql = f"UPDATE families SET {', '.join(updates)} WHERE id = %s"
        params.append(family_id)
        execute_query(sql, tuple(params), commit=True)

    log_audit_event(
        user_id=current_user['user_id'],
        action="FAMILY_UPDATED",
        details={"family_id": family_id, "updated_fields": list(payload.keys())}
    )

    return True, get_family_by_id(family_id, current_user), 200

def delete_family(family_id, current_user):
    """
    Soft deactivates family (`status = 'INACTIVE'`).
    """
    family = execute_query("SELECT * FROM families WHERE id = %s AND status = 'ACTIVE'", (family_id,), fetchone=True)
    if not family:
        return False, {"message": "Family not found.", "error_code": "NOT_FOUND"}, 404

    execute_query("UPDATE families SET status = 'INACTIVE', updated_at = NOW() WHERE id = %s", (family_id,), commit=True)

    log_audit_event(
        user_id=current_user['user_id'],
        action="FAMILY_DEACTIVATED",
        details={"family_id": family_id, "family_code": family['family_code'], "family_name": family['family_name']}
    )

    return True, {"message": f"Family {family['family_name']} ({family['family_code']}) deactivated successfully."}, 200

from db import execute_query
from utils.validators import validate_mobile
from services.audit_service import log_audit_event

def add_emergency_contact(person_id, payload, current_user):
    contact_name = payload.get('contact_name', '').strip()
    relationship = payload.get('relationship', 'Relative').strip()
    mobile = payload.get('mobile', '').strip()
    alternate_mobile = payload.get('alternate_mobile', '').strip() or None
    is_primary = 1 if payload.get('is_primary') else 0

    if not contact_name:
        return False, {"message": "Contact Name is required.", "error_code": "INVALID_NAME"}, 400

    valid_mob, mob_res = validate_mobile(mobile)
    if not valid_mob:
        return False, {"message": mob_res, "error_code": "INVALID_MOBILE"}, 400

    if is_primary:
        execute_query("UPDATE emergency_contacts SET is_primary = 0 WHERE person_id = %s", (person_id,), commit=True)

    contact_id = execute_query("""
    INSERT INTO emergency_contacts (person_id, contact_name, relationship, mobile, alternate_mobile, is_primary)
    VALUES (%s, %s, %s, %s, %s, %s)
    """, (person_id, contact_name, relationship, mob_res, alternate_mobile, is_primary), commit=True)

    log_audit_event(
        user_id=current_user['user_id'],
        action="EMERGENCY_CONTACT_UPDATED",
        details={"person_id": person_id, "contact_id": contact_id, "contact_name": contact_name}
    )

    return True, {"contact_id": contact_id, "contact_name": contact_name, "mobile": mob_res}, 201

def update_emergency_contact(person_id, contact_id, payload, current_user):
    contact = execute_query("SELECT * FROM emergency_contacts WHERE id = %s AND person_id = %s", (contact_id, person_id), fetchone=True)
    if not contact:
        return False, {"message": "Emergency contact not found.", "error_code": "NOT_FOUND"}, 404

    updates = []
    params = []

    if 'contact_name' in payload and payload['contact_name'].strip():
        updates.append("contact_name = %s")
        params.append(payload['contact_name'].strip())

    if 'relationship' in payload:
        updates.append("relationship = %s")
        params.append(payload['relationship'].strip())

    if 'mobile' in payload and payload['mobile'].strip():
        valid_m, mob_res = validate_mobile(payload['mobile'])
        if not valid_m:
            return False, {"message": mob_res, "error_code": "INVALID_MOBILE"}, 400
        updates.append("mobile = %s")
        params.append(mob_res)

    if 'alternate_mobile' in payload:
        updates.append("alternate_mobile = %s")
        params.append(payload['alternate_mobile'].strip() if payload['alternate_mobile'] else None)

    if updates:
        updates.append("updated_at = NOW()")
        sql = f"UPDATE emergency_contacts SET {', '.join(updates)} WHERE id = %s"
        params.append(contact_id)
        execute_query(sql, tuple(params), commit=True)

    log_audit_event(
        user_id=current_user['user_id'],
        action="EMERGENCY_CONTACT_UPDATED",
        details={"person_id": person_id, "contact_id": contact_id}
    )

    return True, {"message": "Emergency contact updated successfully."}, 200

def delete_emergency_contact(person_id, contact_id, current_user):
    contact = execute_query("SELECT * FROM emergency_contacts WHERE id = %s AND person_id = %s", (contact_id, person_id), fetchone=True)
    if not contact:
        return False, {"message": "Emergency contact not found.", "error_code": "NOT_FOUND"}, 404

    execute_query("DELETE FROM emergency_contacts WHERE id = %s", (contact_id,), commit=True)

    log_audit_event(
        user_id=current_user['user_id'],
        action="EMERGENCY_CONTACT_DELETED",
        details={"person_id": person_id, "contact_id": contact_id}
    )

    return True, {"message": "Emergency contact removed successfully."}, 200

from flask import jsonify, request
from db import execute_query

def verify_family_access(family_id, current_user, required_level='VIEWER'):
    """
    Verifies that the authenticated user owns or has access to the given family.
    SUPER_ADMIN bypasses ownership check.
    Returns: (is_allowed, family_record)
    """
    if not current_user:
        return False, None

    user_id = current_user['user_id']
    role_name = current_user['role_name']

    # Fetch family record
    family = execute_query("SELECT * FROM families WHERE id = %s AND status = 'ACTIVE'", (family_id,), fetchone=True)
    if not family:
        return False, None

    # Super Admin or Event Admin bypass
    if role_name in ['SUPER_ADMIN', 'EVENT_ADMIN']:
        return True, family

    # Direct owner check
    if family['owner_user_id'] == user_id:
        return True, family

    # Family access table check
    access = execute_query(
        "SELECT access_level FROM family_access WHERE family_id = %s AND user_id = %s AND status = 'ACTIVE'",
        (family_id, user_id),
        fetchone=True
    )
    if not access:
        return False, None

    level_hierarchy = {'VIEWER': 1, 'EDITOR': 2, 'OWNER': 3}
    user_level = level_hierarchy.get(access['access_level'], 0)
    req_level = level_hierarchy.get(required_level, 1)

    if user_level >= req_level:
        return True, family

    return False, None

def verify_person_access(person_id, current_user, required_level='VIEWER'):
    """
    Verifies if authenticated user is authorized to view or edit a person profile.
    Checks family association of the person.
    Returns: (is_allowed, person_record, family_record)
    """
    if not current_user:
        return False, None, None

    # Fetch person record
    person = execute_query("SELECT * FROM person_profiles WHERE id = %s", (person_id,), fetchone=True)
    if not person:
        return False, None, None

    # Super admin / Police / Help Center / Medical bypass for restricted operations
    if current_user['role_name'] in ['SUPER_ADMIN', 'EVENT_ADMIN', 'POLICE_OFFICER', 'MEDICAL_STAFF', 'HELP_CENTER_OPERATOR']:
        return True, person, None

    # Find associated family
    fm = execute_query("SELECT family_id FROM family_members WHERE person_id = %s AND status = 'ACTIVE'", (person_id,), fetchone=True)
    if not fm:
        return False, person, None

    allowed, family = verify_family_access(fm['family_id'], current_user, required_level)
    return allowed, person, family

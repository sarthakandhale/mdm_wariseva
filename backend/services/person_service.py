import uuid
from datetime import datetime, date
from db import execute_query
from services.audit_service import log_audit_event

def calculate_age(dob_str):
    """
    Calculates exact age in years from date of birth string (YYYY-MM-DD).
    """
    if isinstance(dob_str, str):
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
    elif isinstance(dob_str, date):
        dob = dob_str
    else:
        return 0

    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return max(0, age)

def determine_age_category(age):
    """
    Classifies age into system categories:
    0-12: CHILD
    13-17: MINOR
    18-59: ADULT
    60+: ELDERLY
    """
    if age <= 12:
        return 'CHILD'
    elif age <= 17:
        return 'MINOR'
    elif age <= 59:
        return 'ADULT'
    else:
        return 'ELDERLY'

def generate_person_code():
    """Generates unique Person ID code: RY-PER-2026-XXXXXX"""
    res = execute_query("SELECT COUNT(*) as cnt FROM person_profiles", fetchone=True)
    next_num = (res['cnt'] if res else 0) + 1
    return f"RY-PER-2026-{next_num:06d}"

def create_person_profile(family_id, payload, current_user):
    """
    Creates a full person profile including physical, clothing, safety, and relationship to family.
    """
    full_name = payload.get('full_name', '').strip()
    dob_str = payload.get('date_of_birth')
    gender = payload.get('gender', 'MALE').upper()
    relationship = payload.get('relationship', 'Relative')

    if not full_name or len(full_name) < 2:
        return False, {"message": "Full Name is required and must be at least 2 characters.", "error_code": "INVALID_NAME"}, 400

    if not dob_str:
        return False, {"message": "Date of Birth is required.", "error_code": "INVALID_DOB"}, 400

    try:
        age = calculate_age(dob_str)
    except Exception:
        return False, {"message": "Invalid Date of Birth format. Use YYYY-MM-DD.", "error_code": "INVALID_DOB"}, 400

    age_category = determine_age_category(age)
    person_code = generate_person_code()
    per_uuid = f"per-{uuid.uuid4().hex[:12]}"

    # Insert into person_profiles
    p_sql = """
    INSERT INTO person_profiles (
        uuid, person_code, full_name, date_of_birth, gender, age_category,
        height, approx_weight, hair_color, eye_color, skin_tone, identification_mark,
        glasses, hearing_aid, walking_assistance, preferred_language, profile_visibility, status
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    person_id = execute_query(p_sql, (
        per_uuid, person_code, full_name, dob_str, gender, age_category,
        payload.get('height'), payload.get('approx_weight'), payload.get('hair_color'),
        payload.get('eye_color'), payload.get('skin_tone'), payload.get('identification_mark'),
        1 if payload.get('glasses') else 0,
        1 if payload.get('hearing_aid') else 0,
        1 if payload.get('walking_assistance') else 0,
        payload.get('preferred_language', 'en'),
        payload.get('profile_visibility', 'PRIVATE'),
        'ACTIVE'
    ), commit=True)

    # Link to family_members
    fm_uuid = f"fm-{uuid.uuid4().hex[:12]}"
    execute_query("""
    INSERT INTO family_members (uuid, family_id, person_id, relationship_type, status)
    VALUES (%s, %s, %s, %s, 'ACTIVE')
    """, (fm_uuid, family_id, person_id, relationship), commit=True)

    # Insert Clothing Profile if provided
    if any(k in payload for k in ['top_type', 'bottom_type', 'clothing_description']):
        execute_query("""
        INSERT INTO clothing_profiles (person_id, top_type, top_color, bottom_type, bottom_color, footwear, footwear_color, headwear, accessories, description)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            person_id, payload.get('top_type'), payload.get('top_color'),
            payload.get('bottom_type'), payload.get('bottom_color'),
            payload.get('footwear'), payload.get('footwear_color'),
            payload.get('headwear'), payload.get('accessories'), payload.get('clothing_description')
        ), commit=True)

    # Insert Safety Profile if provided
    if any(k in payload for k in ['medical_condition', 'allergy_information', 'blood_group']):
        execute_query("""
        INSERT INTO person_safety_profiles (
            person_id, medical_condition, medication_requirement, allergy_information,
            blood_group, mobility_assistance, communication_difficulty, cognitive_assistance_required, consent_status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            person_id, payload.get('medical_condition'), payload.get('medication_requirement'),
            payload.get('allergy_information'), payload.get('blood_group'),
            payload.get('mobility_assistance'), payload.get('communication_difficulty'),
            1 if payload.get('cognitive_assistance_required') else 0,
            1 if payload.get('consent_given') else 0
        ), commit=True)

    # Insert Primary Emergency Contact if provided
    if payload.get('emergency_contact_name') and payload.get('emergency_contact_mobile'):
        execute_query("""
        INSERT INTO emergency_contacts (person_id, contact_name, relationship, mobile, alternate_mobile, is_primary)
        VALUES (%s, %s, %s, %s, %s, 1)
        """, (
            person_id, payload.get('emergency_contact_name'), payload.get('emergency_relationship', 'Guardian'),
            payload.get('emergency_contact_mobile'), payload.get('emergency_alternate_mobile')
        ), commit=True)

    # Log Audit Event
    log_audit_event(
        user_id=current_user['user_id'],
        action="MEMBER_ADDED",
        details={"family_id": family_id, "person_id": person_id, "person_code": person_code, "name": full_name, "age_category": age_category}
    )

    return True, get_person_full_profile(person_id), 201

def get_person_full_profile(person_id, current_user=None):
    """
    Retrieves aggregated person profile data with calculated age and sensitive safety masking.
    """
    person = execute_query("SELECT * FROM person_profiles WHERE id = %s", (person_id,), fetchone=True)
    if not person:
        return None

    # Calculate real-time age
    calculated_age = calculate_age(person['date_of_birth'])
    person['calculated_age'] = calculated_age

    # Fetch Photos
    photos = execute_query("SELECT * FROM person_photos WHERE person_id = %s ORDER BY is_primary DESC, id DESC", (person_id,), fetchall=True)
    person['photos'] = photos
    person['primary_photo'] = photos[0]['file_path'] if photos else None

    # Fetch Clothing Profile
    clothing = execute_query("SELECT * FROM clothing_profiles WHERE person_id = %s", (person_id,), fetchone=True)
    person['clothing'] = clothing or {}

    # Fetch Safety Profile
    safety = execute_query("SELECT * FROM person_safety_profiles WHERE person_id = %s", (person_id,), fetchone=True)
    person['safety'] = safety or {}

    # Fetch Emergency Contacts
    emergency = execute_query("SELECT * FROM emergency_contacts WHERE person_id = %s ORDER BY is_primary DESC", (person_id,), fetchall=True)
    person['emergency_contacts'] = emergency or []

    # Fetch Family Relationship
    fm = execute_query("""
    SELECT fm.relationship_type, f.id as family_id, f.family_name, f.family_code 
    FROM family_members fm
    JOIN families f ON fm.family_id = f.id
    WHERE fm.person_id = %s AND fm.status = 'ACTIVE'
    """, (person_id,), fetchone=True)
    person['family'] = fm or {}

    # Audit Logging for viewing sensitive safety data if logged in
    if current_user and safety and any(safety.values()):
        log_audit_event(
            user_id=current_user['user_id'],
            action="SAFETY_INFO_VIEWED",
            details={"person_id": person_id, "person_code": person['person_code']}
        )

    return person

def update_person_profile(person_id, payload, current_user):
    """
    Updates person profile fields. Disallows modifying person_code, id, or created_at.
    """
    person = execute_query("SELECT * FROM person_profiles WHERE id = %s", (person_id,), fetchone=True)
    if not person:
        return False, {"message": "Person profile not found.", "error_code": "NOT_FOUND"}, 404

    updates = []
    params = []

    if 'full_name' in payload and payload['full_name'].strip():
        updates.append("full_name = %s")
        params.append(payload['full_name'].strip())

    if 'date_of_birth' in payload and payload['date_of_birth']:
        dob_str = payload['date_of_birth']
        new_age = calculate_age(dob_str)
        new_cat = determine_age_category(new_age)
        updates.append("date_of_birth = %s")
        params.append(dob_str)
        updates.append("age_category = %s")
        params.append(new_cat)

    if 'gender' in payload:
        updates.append("gender = %s")
        params.append(payload['gender'].upper())

    for field in ['height', 'approx_weight', 'hair_color', 'eye_color', 'skin_tone', 'identification_mark', 'preferred_language', 'profile_visibility']:
        if field in payload:
            updates.append(f"{field} = %s")
            params.append(payload[field])

    for bool_field in ['glasses', 'hearing_aid', 'walking_assistance']:
        if bool_field in payload:
            updates.append(f"{bool_field} = %s")
            params.append(1 if payload[bool_field] else 0)

    if updates:
        updates.append("updated_at = NOW()")
        sql = f"UPDATE person_profiles SET {', '.join(updates)} WHERE id = %s"
        params.append(person_id)
        execute_query(sql, tuple(params), commit=True)

    # Update Clothing if present
    if any(k in payload for k in ['top_type', 'top_color', 'bottom_type', 'bottom_color', 'footwear', 'headwear', 'accessories', 'clothing_description']):
        existing_c = execute_query("SELECT id FROM clothing_profiles WHERE person_id = %s", (person_id,), fetchone=True)
        if existing_c:
            execute_query("""
            UPDATE clothing_profiles SET top_type = %s, top_color = %s, bottom_type = %s, bottom_color = %s,
            footwear = %s, footwear_color = %s, headwear = %s, accessories = %s, description = %s, updated_at = NOW()
            WHERE person_id = %s
            """, (
                payload.get('top_type'), payload.get('top_color'), payload.get('bottom_type'), payload.get('bottom_color'),
                payload.get('footwear'), payload.get('footwear_color'), payload.get('headwear'), payload.get('accessories'), payload.get('clothing_description'),
                person_id
            ), commit=True)
        else:
            execute_query("""
            INSERT INTO clothing_profiles (person_id, top_type, top_color, bottom_type, bottom_color, footwear, footwear_color, headwear, accessories, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                person_id, payload.get('top_type'), payload.get('top_color'), payload.get('bottom_type'), payload.get('bottom_color'),
                payload.get('footwear'), payload.get('footwear_color'), payload.get('headwear'), payload.get('accessories'), payload.get('clothing_description')
            ), commit=True)

    # Update Safety Profile if present
    if any(k in payload for k in ['medical_condition', 'medication_requirement', 'allergy_information', 'blood_group', 'mobility_assistance', 'communication_difficulty']):
        existing_s = execute_query("SELECT id FROM person_safety_profiles WHERE person_id = %s", (person_id,), fetchone=True)
        if existing_s:
            execute_query("""
            UPDATE person_safety_profiles SET medical_condition = %s, medication_requirement = %s, allergy_information = %s,
            blood_group = %s, mobility_assistance = %s, communication_difficulty = %s, cognitive_assistance_required = %s, consent_status = %s, updated_at = NOW()
            WHERE person_id = %s
            """, (
                payload.get('medical_condition'), payload.get('medication_requirement'), payload.get('allergy_information'),
                payload.get('blood_group'), payload.get('mobility_assistance'), payload.get('communication_difficulty'),
                1 if payload.get('cognitive_assistance_required') else 0,
                1 if payload.get('consent_given') else 0,
                person_id
            ), commit=True)

    log_audit_event(
        user_id=current_user['user_id'],
        action="MEMBER_UPDATED",
        details={"person_id": person_id, "updated_fields": list(payload.keys())}
    )

    return True, get_person_full_profile(person_id, current_user), 200

def deactivate_person(person_id, current_user):
    """
    Soft deactivates a person profile (status = 'INACTIVE'). Does not hard delete records.
    """
    person = execute_query("SELECT * FROM person_profiles WHERE id = %s", (person_id,), fetchone=True)
    if not person:
        return False, {"message": "Person profile not found.", "error_code": "NOT_FOUND"}, 404

    execute_query("UPDATE person_profiles SET status = 'INACTIVE', updated_at = NOW() WHERE id = %s", (person_id,), commit=True)
    execute_query("UPDATE family_members SET status = 'INACTIVE', updated_at = NOW() WHERE person_id = %s", (person_id,), commit=True)

    log_audit_event(
        user_id=current_user['user_id'],
        action="MEMBER_DEACTIVATED",
        details={"person_id": person_id, "person_code": person['person_code'], "full_name": person['full_name']}
    )

    return True, {"message": f"Person profile {person['full_name']} ({person['person_code']}) deactivated successfully."}, 200

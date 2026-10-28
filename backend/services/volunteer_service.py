import uuid
from datetime import datetime
from db import execute_query
from services.audit_service import log_audit_event

def generate_volunteer_code():
    res = execute_query("SELECT COUNT(*) as cnt FROM volunteers", fetchone=True)
    next_num = (res['cnt'] if res else 0) + 1
    return f"WS-VOL-2026-{next_num:06d}"

def generate_task_code():
    res = execute_query("SELECT COUNT(*) as cnt FROM volunteer_tasks", fetchone=True)
    next_num = (res['cnt'] if res else 0) + 1
    return f"WS-TASK-2026-{next_num:06d}"

def register_volunteer(payload, current_user):
    user_id = current_user['user_id']
    vol_code = generate_volunteer_code()
    vol_uuid = f"vol-{uuid.uuid4().hex[:12]}"

    person_id = payload.get('person_id')
    exp_years = int(payload.get('experience_years', 1))
    pref_zone = payload.get('preferred_zone', 'Saswad').strip()
    emerg_contact = payload.get('emergency_contact', current_user.get('mobile', '')).strip()

    vol_id = execute_query("""
    INSERT INTO volunteers (
        uuid, volunteer_code, user_id, person_id, status, verification_status,
        experience_years, preferred_zone, emergency_contact
    ) VALUES (%s, %s, %s, %s, 'PENDING_VERIFICATION', 'PENDING', %s, %s, %s)
    """, (vol_uuid, vol_code, user_id, person_id, exp_years, pref_zone, emerg_contact), commit=True)

    # Insert Skills if provided
    skills = payload.get('skills', [])
    for s in skills:
        execute_query("""
        INSERT INTO volunteer_skills (volunteer_id, skill_name, skill_level, verified)
        VALUES (%s, %s, %s, 1)
        """, (vol_id, s.get('skill_name', 'GENERAL'), s.get('skill_level', 'INTERMEDIATE')), commit=True)

    # Insert Languages if provided
    languages = payload.get('languages', ['Marathi', 'Hindi'])
    for lang in languages:
        execute_query("""
        INSERT INTO volunteer_languages (volunteer_id, language, proficiency)
        VALUES (%s, %s, 'ADVANCED')
        """, (vol_id, lang if isinstance(lang, str) else lang.get('language', 'Marathi')), commit=True)

    log_audit_event(user_id, "VOLUNTEER_REGISTERED", {"volunteer_id": vol_id, "volunteer_code": vol_code})
    return True, get_volunteer_details(vol_id), 201

def verify_volunteer(volunteer_id, status, notes, current_user):
    user_id = current_user['user_id']
    execute_query("""
    UPDATE volunteers SET verification_status = %s, status = 'ACTIVE', updated_at = NOW() WHERE id = %s
    """, (status, volunteer_id), commit=True)

    log_audit_event(user_id, "VOLUNTEER_VERIFIED", {"volunteer_id": volunteer_id, "status": status, "notes": notes})
    return True, {"message": f"Volunteer verification set to {status}."}, 200

def get_volunteer_details(volunteer_id):
    vol = execute_query("""
    SELECT v.*, u.full_name, u.mobile, u.email, u.profile_photo
    FROM volunteers v
    JOIN users u ON v.user_id = u.id
    WHERE v.id = %s
    """, (volunteer_id,), fetchone=True)

    if not vol:
        return None

    vol['skills'] = execute_query("SELECT * FROM volunteer_skills WHERE volunteer_id = %s", (volunteer_id,), fetchall=True) or []
    vol['languages'] = execute_query("SELECT * FROM volunteer_languages WHERE volunteer_id = %s", (volunteer_id,), fetchall=True) or []
    vol['active_task_count'] = execute_query("""
    SELECT COUNT(*) as cnt FROM volunteer_task_assignments
    WHERE volunteer_id = %s AND status IN ('ASSIGNED', 'ACCEPTED', 'IN_PROGRESS')
    """, (volunteer_id,), fetchone=True)['cnt']

    return vol

def list_volunteers(zone=None, status=None, skill=None):
    where_clauses = []
    params = []

    if zone:
        where_clauses.append("v.preferred_zone = %s")
        params.append(zone)
    if status:
        where_clauses.append("v.status = %s")
        params.append(status)

    where_str = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    return execute_query(f"""
    SELECT v.id, v.volunteer_code, v.status, v.verification_status, v.preferred_zone, u.full_name, u.mobile, u.email
    FROM volunteers v
    JOIN users u ON v.user_id = u.id
    {where_str}
    ORDER BY v.id ASC
    """, tuple(params), fetchall=True) or []

def create_volunteer_task(payload, current_user):
    user_id = current_user['user_id']
    task_code = generate_task_code()
    task_uuid = f"task-{uuid.uuid4().hex[:12]}"

    title = payload.get('title', 'Volunteer Assistance Task').strip()
    desc = payload.get('description', '').strip()
    t_type = payload.get('task_type', 'GENERAL_SUPPORT')
    prio = payload.get('priority', 'MEDIUM')
    source_mod = payload.get('source_module', 'MANUAL')
    source_case = payload.get('source_case_id', '')
    zone = payload.get('zone', 'Saswad').strip()
    lat = payload.get('latitude')
    lon = payload.get('longitude')

    task_id = execute_query("""
    INSERT INTO volunteer_tasks (
        uuid, task_code, title, description, task_type, priority,
        source_module, source_case_id, zone, latitude, longitude, status, created_by
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'UNASSIGNED', %s)
    """, (task_uuid, task_code, title, desc, t_type, prio, source_mod, source_case, zone, lat, lon, user_id), commit=True)

    # Insert Requirements if provided
    req_skill = payload.get('required_skill', 'GENERAL')
    req_lang = payload.get('required_language', 'Marathi')
    execute_query("""
    INSERT INTO volunteer_task_requirements (task_id, required_skill, minimum_skill_level, required_language, quantity)
    VALUES (%s, %s, 'INTERMEDIATE', %s, 1)
    """, (task_id, req_skill, req_lang), commit=True)

    log_audit_event(user_id, "TASK_CREATED", {"task_id": task_id, "task_code": task_code, "priority": prio})
    return True, get_task_details(task_id), 201

def get_task_details(task_id):
    task = execute_query("SELECT * FROM volunteer_tasks WHERE id = %s", (task_id,), fetchone=True)
    if not task:
        return None

    task['requirements'] = execute_query("SELECT * FROM volunteer_task_requirements WHERE task_id = %s", (task_id,), fetchall=True) or []
    task['assignment'] = execute_query("""
    SELECT a.*, v.volunteer_code, u.full_name as volunteer_name, u.mobile as volunteer_mobile
    FROM volunteer_task_assignments a
    JOIN volunteers v ON a.volunteer_id = v.id
    JOIN users u ON v.user_id = u.id
    WHERE a.task_id = %s AND a.status IN ('ASSIGNED', 'ACCEPTED', 'IN_PROGRESS', 'COMPLETED', 'VERIFIED')
    ORDER BY a.id DESC LIMIT 1
    """, (task_id,), fetchone=True)

    return task

def generate_task_recommendations(task_id):
    """
    100% Weighted Rule-Based Recommendation Engine:
    - Skill Match: 30%
    - Zone Match: 20%
    - Availability Match: 15%
    - Language Match: 15%
    - Workload Balance: 10%
    - Experience Level: 10%
    """
    task = get_task_details(task_id)
    if not task:
        return []

    reqs = task.get('requirements', [{}])[0]
    req_skill = reqs.get('required_skill', '')
    req_lang = reqs.get('required_language', 'Marathi')
    task_zone = task.get('zone', 'Saswad')

    candidates = list_volunteers()
    recommendations = []

    for c in candidates:
        vol_id = c['id']
        vol_details = get_volunteer_details(vol_id)

        # 1. Skill Score (30%)
        skill_score = 0
        for s in vol_details.get('skills', []):
            if s['skill_name'].upper() == req_skill.upper():
                skill_score = 30
                break

        # 2. Zone Score (20%)
        zone_score = 20 if vol_details.get('preferred_zone') == task_zone else 8

        # 3. Availability Score (15%)
        avail_score = 15 if vol_details.get('status') in ('ACTIVE', 'AVAILABLE') else 5

        # 4. Language Score (15%)
        lang_score = 0
        for l in vol_details.get('languages', []):
            if l['language'].upper() == req_lang.upper():
                lang_score = 15
                break

        # 5. Workload Score (10%)
        active_tasks = vol_details.get('active_task_count', 0)
        workload_score = 10 if active_tasks == 0 else (7 if active_tasks == 1 else (4 if active_tasks == 2 else 0))

        # 6. Experience Score (10%)
        exp = vol_details.get('experience_years', 1)
        exp_score = 10 if exp >= 3 else (7 if exp >= 1 else 4)

        total_score = skill_score + zone_score + avail_score + lang_score + workload_score + exp_score

        # Save recommendation record
        execute_query("""
        INSERT INTO volunteer_recommendations (
            task_id, volunteer_id, skill_score, location_score, availability_score,
            language_score, workload_score, experience_score, total_score, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'RECOMMENDED')
        """, (task_id, vol_id, skill_score, zone_score, avail_score, lang_score, workload_score, exp_score, total_score), commit=True)

        recommendations.append({
            "volunteer_id": vol_id,
            "volunteer_code": c['volunteer_code'],
            "volunteer_name": c['full_name'],
            "preferred_zone": c['preferred_zone'],
            "total_score": total_score,
            "breakdown": {
                "skill": skill_score,
                "zone": zone_score,
                "availability": avail_score,
                "language": lang_score,
                "workload": workload_score,
                "experience": exp_score
            }
        })

    recommendations.sort(key=lambda x: x['total_score'], reverse=True)
    return recommendations

def assign_task(task_id, volunteer_id, current_user):
    """Assigns task to volunteer with workload cap check (max 3 active tasks)"""
    vol = get_volunteer_details(volunteer_id)
    if not vol:
        return False, {"message": "Volunteer not found."}, 404

    if vol.get('active_task_count', 0) >= 3:
        return False, {"message": "Volunteer has reached maximum active workload capacity (3 tasks).", "error_code": "WORKLOAD_EXCEEDED"}, 400

    execute_query("""
    INSERT INTO volunteer_task_assignments (task_id, volunteer_id, assigned_by, status)
    VALUES (%s, %s, %s, 'ASSIGNED')
    """, (task_id, volunteer_id, current_user['user_id']), commit=True)

    execute_query("UPDATE volunteer_tasks SET status = 'ASSIGNED', updated_at = NOW() WHERE id = %s", (task_id,), commit=True)
    log_audit_event(current_user['user_id'], "TASK_ASSIGNED", {"task_id": task_id, "volunteer_id": volunteer_id})
    return True, {"message": f"Task assigned to Volunteer {vol['volunteer_code']}."}, 200

def accept_task(task_id, volunteer_id, current_user):
    execute_query("""
    UPDATE volunteer_task_assignments SET status = 'ACCEPTED', accepted_at = NOW()
    WHERE task_id = %s AND volunteer_id = %s
    """, (task_id, volunteer_id), commit=True)

    execute_query("UPDATE volunteer_tasks SET status = 'ACCEPTED', updated_at = NOW() WHERE id = %s", (task_id,), commit=True)
    log_audit_event(current_user['user_id'], "TASK_ACCEPTED", {"task_id": task_id, "volunteer_id": volunteer_id})
    return True, {"message": "Task accepted by volunteer."}, 200

def decline_task(task_id, volunteer_id, reason, current_user):
    execute_query("""
    UPDATE volunteer_task_assignments SET status = 'DECLINED', declined_at = NOW(), decline_reason = %s
    WHERE task_id = %s AND volunteer_id = %s
    """, (reason, task_id, volunteer_id), commit=True)

    execute_query("UPDATE volunteer_tasks SET status = 'UNASSIGNED', updated_at = NOW() WHERE id = %s", (task_id,), commit=True)
    log_audit_event(current_user['user_id'], "TASK_DECLINED", {"task_id": task_id, "volunteer_id": volunteer_id, "reason": reason})
    return True, {"message": "Task declined by volunteer."}, 200

def complete_task(task_id, volunteer_id, notes, current_user):
    execute_query("""
    UPDATE volunteer_task_assignments SET status = 'COMPLETED', completed_at = NOW()
    WHERE task_id = %s AND volunteer_id = %s
    """, (task_id, volunteer_id), commit=True)

    execute_query("UPDATE volunteer_tasks SET status = 'COMPLETED', completed_at = NOW(), updated_at = NOW() WHERE id = %s", (task_id,), commit=True)
    log_audit_event(current_user['user_id'], "TASK_COMPLETED", {"task_id": task_id, "volunteer_id": volunteer_id})
    return True, {"message": "Task marked as completed by volunteer. Awaiting coordinator verification."}, 200

def verify_task_completion(task_id, current_user):
    execute_query("""
    UPDATE volunteer_task_assignments SET status = 'VERIFIED' WHERE task_id = %s
    """, (task_id,), commit=True)

    execute_query("UPDATE volunteer_tasks SET status = 'VERIFIED', updated_at = NOW() WHERE id = %s", (task_id,), commit=True)
    log_audit_event(current_user['user_id'], "TASK_VERIFIED", {"task_id": task_id})
    return True, {"message": "Task completion verified by coordinator."}, 200

def volunteer_check_in(volunteer_id, shift_id, current_user):
    att_id = execute_query("""
    INSERT INTO volunteer_attendance (volunteer_id, shift_id, status)
    VALUES (%s, %s, 'ON_DUTY')
    """, (volunteer_id, shift_id), commit=True)

    execute_query("UPDATE volunteers SET status = 'ACTIVE' WHERE id = %s", (volunteer_id,), commit=True)
    log_audit_event(current_user['user_id'], "VOLUNTEER_CHECKED_IN", {"volunteer_id": volunteer_id})
    return True, {"message": "Volunteer checked in for shift.", "attendance_id": att_id}, 201

def volunteer_check_out(volunteer_id, current_user):
    execute_query("""
    UPDATE volunteer_attendance SET check_out = NOW(), status = 'OFF_DUTY'
    WHERE volunteer_id = %s AND check_out IS NULL
    """, (volunteer_id,), commit=True)

    execute_query("UPDATE volunteers SET status = 'OFFLINE' WHERE id = %s", (volunteer_id,), commit=True)
    log_audit_event(current_user['user_id'], "VOLUNTEER_CHECKED_OUT", {"volunteer_id": volunteer_id})
    return True, {"message": "Volunteer checked out."}, 200

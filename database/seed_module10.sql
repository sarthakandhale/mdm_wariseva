-- ====================================================================
-- WariSeva Platform - Module 10: Seed Data
-- Case Study: Alandi–Pandharpur Dindi Wari, Maharashtra
-- ====================================================================

USE reuniteai;

-- --------------------------------------------------------------------
-- 1. SEED VOLUNTEERS
-- --------------------------------------------------------------------
INSERT INTO volunteers (id, uuid, volunteer_code, user_id, person_id, status, verification_status, experience_years, preferred_zone, emergency_contact) VALUES
(1, 'vol-001', 'WS-VOL-2026-000001', 6, 1, 'ACTIVE', 'VERIFIED', 3, 'Saswad', '+91 98220 99001'),
(2, 'vol-002', 'WS-VOL-2026-000002', 8, NULL, 'ACTIVE', 'VERIFIED', 1, 'Saswad', '+91 98220 99002');

-- --------------------------------------------------------------------
-- 2. SEED VOLUNTEER SKILLS
-- --------------------------------------------------------------------
INSERT INTO volunteer_skills (volunteer_id, skill_name, skill_level, verified, verified_by) VALUES
(1, 'FIRST_AID', 'CERTIFIED', 1, 1),
(1, 'CROWD_MANAGEMENT', 'ADVANCED', 1, 1),
(1, 'CHILD_ASSISTANCE', 'ADVANCED', 1, 1),
(2, 'LANGUAGE_SUPPORT', 'INTERMEDIATE', 1, 1);

-- --------------------------------------------------------------------
-- 3. SEED VOLUNTEER LANGUAGES
-- --------------------------------------------------------------------
INSERT INTO volunteer_languages (volunteer_id, language, proficiency) VALUES
(1, 'Marathi', 'NATIVE'),
(1, 'Hindi', 'ADVANCED'),
(1, 'English', 'INTERMEDIATE'),
(2, 'Odia', 'NATIVE');

-- --------------------------------------------------------------------
-- 4. SEED SHIFTS
-- --------------------------------------------------------------------
INSERT INTO volunteer_shifts (id, shift_code, name, start_time, end_time, zone, status) VALUES
(1, 'SHIFT-MNG-01', 'Morning Shift (06:00 - 14:00)', '06:00', '14:00', 'Saswad', 'ACTIVE'),
(2, 'SHIFT-AFT-02', 'Afternoon Shift (14:00 - 22:00)', '14:00', '22:00', 'Saswad', 'ACTIVE');

-- --------------------------------------------------------------------
-- 5. SEED VOLUNTEER TEAMS
-- --------------------------------------------------------------------
INSERT INTO volunteer_teams (id, team_code, name, team_type, leader_id, zone, status) VALUES
(1, 'TEAM-MED-01', 'Saswad First Aid Response Team', 'MEDICAL', 1, 'Saswad', 'ACTIVE');

INSERT INTO volunteer_team_members (team_id, volunteer_id, role, status) VALUES
(1, 1, 'LEADER', 'ACTIVE'),
(1, 2, 'MEMBER', 'ACTIVE');

-- --------------------------------------------------------------------
-- 6. SEED VOLUNTEER TASKS
-- --------------------------------------------------------------------
INSERT INTO volunteer_tasks (
    id, uuid, task_code, title, description, task_type, priority,
    source_module, source_case_id, zone, route_section, latitude, longitude, status, created_by
) VALUES
(1, 'task-001', 'WS-TASK-2026-000001', 'Lost Child Search Assistance near Saswad Water Station', 'Assist help center operator in searching for missing child Aarav near Saswad Rest Spot 3', 'LOST_PERSON_SEARCH', 'HIGH', 'MODULE_4', 'WS-LP-2026-000001', 'Saswad', 'Pune -> Saswad', 18.3450000, 74.0320000, 'UNASSIGNED', 1);

-- --------------------------------------------------------------------
-- 7. SEED TASK REQUIREMENTS
-- --------------------------------------------------------------------
INSERT INTO volunteer_task_requirements (task_id, required_skill, minimum_skill_level, required_language, quantity) VALUES
(1, 'CHILD_ASSISTANCE', 'INTERMEDIATE', 'Marathi', 1);

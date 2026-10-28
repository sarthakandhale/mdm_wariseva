-- ====================================================================
-- WariSeva Platform - Module 8: Seed Data
-- Case Study: Alandi–Pandharpur Dindi Wari, Maharashtra
-- ====================================================================

USE reuniteai;

-- --------------------------------------------------------------------
-- 1. SEED DINDIS
-- --------------------------------------------------------------------
INSERT INTO dindis (
    id, uuid, dindi_code, dindi_number, name, description, registration_year, start_location, destination, expected_member_count, status, created_by
) VALUES
(1, 'din-027', 'WS-DIN-2026-000027', 27, 'Shree Sant Tukaram Maharaj Dindi No. 27', 'Official registered Warkari Dindi travelling Alandi-Pandharpur route', 2026, 'Alandi', 'Pandharpur', 250, 'VERIFIED', 1),
(2, 'din-015', 'WS-DIN-2026-000015', 15, 'Shree Dnyaneshwar Maharaj Dindi No. 15', 'Registered Warkari group travelling Pune to Pandharpur', 2026, 'Pune', 'Pandharpur', 180, 'VERIFIED', 1);

-- --------------------------------------------------------------------
-- 2. SEED DINDI LEADERS
-- --------------------------------------------------------------------
INSERT INTO dindi_leaders (id, dindi_id, person_id, user_id, role, status) VALUES
(1, 1, 4, 5, 'PRIMARY_LEADER', 'ACTIVE'),
(2, 2, NULL, 6, 'PRIMARY_LEADER', 'ACTIVE');

-- --------------------------------------------------------------------
-- 3. SEED DINDI MEMBERSHIPS
-- --------------------------------------------------------------------
INSERT INTO dindi_memberships (dindi_id, person_id, membership_number, role, status) VALUES
(1, 1, 'MEM-DIN27-001', 'MEMBER', 'ACTIVE'),
(1, 2, 'MEM-DIN27-002', 'MEMBER', 'ACTIVE'),
(1, 3, 'MEM-DIN27-003', 'MEMBER', 'ACTIVE'),
(1, 4, 'MEM-DIN27-004', 'LEADER', 'ACTIVE');

-- --------------------------------------------------------------------
-- 4. SEED SCHEDULES
-- --------------------------------------------------------------------
INSERT INTO dindi_schedules (dindi_id, schedule_date, start_location, end_location, expected_start_time, expected_arrival_time, rest_point, notes, status) VALUES
(1, '2026-07-01', 'Alandi', 'Pune', '05:30 AM', '06:00 PM', 'Phugewadi Rest Tent', 'Day 1 march towards Pune city halt', 'SCHEDULED'),
(1, '2026-07-02', 'Pune', 'Saswad', '05:00 AM', '06:30 PM', 'Dive Ghat Halt Desk', 'Ascent via Dive Ghat pass', 'SCHEDULED'),
(1, '2026-07-03', 'Saswad', 'Jejuri', '06:00 AM', '05:00 PM', 'Saswad Water Dispenser 3', 'Tea halt at Saswad water station', 'SCHEDULED');

-- --------------------------------------------------------------------
-- 5. SEED ANNOUNCEMENTS
-- --------------------------------------------------------------------
INSERT INTO dindi_announcements (dindi_id, title, message, priority, created_by, status) VALUES
(1, 'Morning Palkhi Departure Time', 'Dindi march will assemble at 05:15 AM near Saswad Halt Water Station. Please form rows.', 'IMPORTANT', 5, 'ACTIVE');

-- --------------------------------------------------------------------
-- 6. SEED CONTACTS
-- --------------------------------------------------------------------
INSERT INTO dindi_contacts (dindi_id, contact_type, contact_name, contact_number, visibility) VALUES
(1, 'PRIMARY', 'Mr. Dindi Leader', '+91 98220 99999', 'PUBLIC'),
(1, 'EMERGENCY', 'Dindi Medical & Helpline Desk', '+91 98220 88888', 'PUBLIC');

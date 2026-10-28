-- ====================================================================
-- ReuniteAI Platform - Module 1: Seed Data
-- Demo Accounts Password for all demo users: Demo1234!
-- Hash generated via Werkzeug generate_password_hash('Demo1234!')
-- ====================================================================

USE reuniteai;

-- Disable foreign key checks for clean seeding
SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE role_permissions;
TRUNCATE TABLE permissions;
TRUNCATE TABLE password_reset_tokens;
TRUNCATE TABLE user_sessions;
TRUNCATE TABLE audit_logs;
TRUNCATE TABLE users;
TRUNCATE TABLE roles;

SET FOREIGN_KEY_CHECKS = 1;

-- --------------------------------------------------------------------
-- 1. SEED ROLES
-- --------------------------------------------------------------------
INSERT INTO roles (id, name, description) VALUES
(1, 'PARENT_GUARDIAN', 'Parent or guardian registering family members and reporting missing persons'),
(2, 'VOLUNTEER', 'Ground volunteer assisting in search, reporting found individuals, and help centers'),
(3, 'POLICE_OFFICER', 'Law enforcement official managing cases, verification, and field coordination'),
(4, 'MEDICAL_STAFF', 'Medical center staff logging unclaimed individuals and healthcare cases'),
(5, 'HELP_CENTER_OPERATOR', 'Kiosk/Help desk staff managing lost & found inquiries and matching'),
(6, 'EVENT_ADMIN', 'Event manager overseeing logistics, staff approvals, and district reports'),
(7, 'SUPER_ADMIN', 'System administrator with full system permissions and security audit access');

-- --------------------------------------------------------------------
-- 2. SEED PERMISSIONS
-- --------------------------------------------------------------------
INSERT INTO permissions (id, name, description) VALUES
(1, 'USER_VIEW', 'View user profiles and list users'),
(2, 'USER_CREATE', 'Register or create new system users'),
(3, 'USER_UPDATE', 'Update user profiles and details'),
(4, 'USER_DELETE', 'Delete or remove users'),
(5, 'PROFILE_VIEW', 'View own profile information'),
(6, 'PROFILE_UPDATE', 'Update own profile information'),
(7, 'CASE_VIEW', 'View missing/found person cases'),
(8, 'CASE_CREATE', 'Report missing person case'),
(9, 'CASE_UPDATE', 'Update missing person case status'),
(10, 'FOUND_PERSON_CREATE', 'Report found person or item'),
(11, 'MATCH_VIEW', 'View AI face and profile match results'),
(12, 'MATCH_VERIFY', 'Confirm or reject person reunification match'),
(13, 'VOLUNTEER_ASSIGN', 'Assign volunteers to active search sectors'),
(14, 'REPORT_VIEW', 'View overall platform reports and analytics'),
(15, 'ADMIN_APPROVE_USER', 'Approve, suspend, block, or reject user registrations'),
(16, 'AUDIT_VIEW', 'View security audit logs and system events');

-- --------------------------------------------------------------------
-- 3. SEED ROLE_PERMISSIONS
-- --------------------------------------------------------------------

-- PARENT_GUARDIAN
INSERT INTO role_permissions (role_id, permission_id) VALUES
(1, 5), -- PROFILE_VIEW
(1, 6), -- PROFILE_UPDATE
(1, 7), -- CASE_VIEW
(1, 8), -- CASE_CREATE
(1, 9); -- CASE_UPDATE

-- VOLUNTEER
INSERT INTO role_permissions (role_id, permission_id) VALUES
(2, 5), -- PROFILE_VIEW
(2, 6), -- PROFILE_UPDATE
(2, 7), -- CASE_VIEW
(2, 10),-- FOUND_PERSON_CREATE
(2, 11);-- MATCH_VIEW

-- POLICE_OFFICER
INSERT INTO role_permissions (role_id, permission_id) VALUES
(3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (3, 10), (3, 11), (3, 12), (3, 13), (3, 14);

-- MEDICAL_STAFF
INSERT INTO role_permissions (role_id, permission_id) VALUES
(4, 5), (4, 6), (4, 7), (4, 10), (4, 11);

-- HELP_CENTER_OPERATOR
INSERT INTO role_permissions (role_id, permission_id) VALUES
(5, 5), (5, 6), (5, 7), (5, 8), (5, 9), (5, 10), (5, 11), (5, 12);

-- EVENT_ADMIN
INSERT INTO role_permissions (role_id, permission_id) VALUES
(6, 1), (6, 2), (6, 3), (6, 5), (6, 6), (6, 7), (6, 8), (6, 9), (6, 10), (6, 11), (6, 12), (6, 13), (6, 14), (6, 15);

-- SUPER_ADMIN (All Permissions)
INSERT INTO role_permissions (role_id, permission_id) VALUES
(7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (7, 8), (7, 9), (7, 10), (7, 11), (7, 12), (7, 13), (7, 14), (7, 15), (7, 16);

-- --------------------------------------------------------------------
-- 4. SEED DEMO USERS
-- Password for all demo accounts: Demo1234!
-- PBKDF2 Werkzeug Hash for 'Demo1234!':
-- pbkdf2:sha256:600000$87vL9aB123$1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b
-- scrypt hash compatibility will be generated dynamically on backend start if missing or matching pbkdf2 hash.
-- --------------------------------------------------------------------

INSERT INTO users (id, uuid, full_name, mobile, email, password_hash, role_id, profile_photo, preferred_language, status, is_verified, created_at) VALUES
(1, 'usr-super-admin-001', 'System Administrator', '9876543210', 'admin@demo.com', 'pbkdf2:sha256:600000$ReuniteAI$6bf0f19c99185a73e0a2982d61b6c7a42ad8bf9cd4043b2a265ae785501f2fbb', 7, NULL, 'en', 'ACTIVE', 1, NOW()),
(2, 'usr-event-admin-002', 'Event Administrator', '9876543211', 'eventadmin@demo.com', 'pbkdf2:sha256:600000$ReuniteAI$6bf0f19c99185a73e0a2982d61b6c7a42ad8bf9cd4043b2a265ae785501f2fbb', 6, NULL, 'en', 'ACTIVE', 1, NOW()),
(3, 'usr-police-003', 'Inspector Rajesh Kumar', '9876543212', 'police@demo.com', 'pbkdf2:sha256:600000$ReuniteAI$6bf0f19c99185a73e0a2982d61b6c7a42ad8bf9cd4043b2a265ae785501f2fbb', 3, NULL, 'or', 'ACTIVE', 1, NOW()),
(4, 'usr-helpdesk-004', 'Sita Sharma (Help Desk)', '9876543213', 'helpcenter@demo.com', 'pbkdf2:sha256:600000$ReuniteAI$6bf0f19c99185a73e0a2982d61b6c7a42ad8bf9cd4043b2a265ae785501f2fbb', 5, NULL, 'or', 'ACTIVE', 1, NOW()),
(5, 'usr-medical-005', 'Dr. Ananya Dash', '9876543214', 'medical@demo.com', 'pbkdf2:sha256:600000$ReuniteAI$6bf0f19c99185a73e0a2982d61b6c7a42ad8bf9cd4043b2a265ae785501f2fbb', 4, NULL, 'en', 'ACTIVE', 1, NOW()),
(6, 'usr-volunteer-006', 'Amitabh Mohanty', '9876543215', 'volunteer@demo.com', 'pbkdf2:sha256:600000$ReuniteAI$6bf0f19c99185a73e0a2982d61b6c7a42ad8bf9cd4043b2a265ae785501f2fbb', 2, NULL, 'hi', 'ACTIVE', 1, NOW()),
(7, 'usr-parent-007', 'Ramesh Chandra Swain', '9876543216', 'parent@demo.com', 'pbkdf2:sha256:600000$ReuniteAI$6bf0f19c99185a73e0a2982d61b6c7a42ad8bf9cd4043b2a265ae785501f2fbb', 1, NULL, 'or', 'ACTIVE', 1, NOW()),
(8, 'usr-volunteer-008', 'Priya Sahoo (Pending)', '9876543217', 'priya.v@demo.com', 'pbkdf2:sha256:600000$ReuniteAI$6bf0f19c99185a73e0a2982d61b6c7a42ad8bf9cd4043b2a265ae785501f2fbb', 2, NULL, 'or', 'PENDING', 0, NOW()),
(9, 'usr-police-009', 'Sub-Inspector Manoj Jena', '9876543218', 'manoj.police@demo.com', 'pbkdf2:sha256:600000$ReuniteAI$6bf0f19c99185a73e0a2982d61b6c7a42ad8bf9cd4043b2a265ae785501f2fbb', 3, NULL, 'or', 'PENDING', 0, NOW());

-- Initial Audit Log Entry
INSERT INTO audit_logs (user_id, action, details, ip_address, user_agent, created_at) VALUES
(1, 'SYSTEM_INIT', 'ReuniteAI System initialized with seed roles and accounts', '127.0.0.1', 'System/Initializer', NOW());

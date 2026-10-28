-- ====================================================================
-- ReuniteAI Platform - Module 2: Seed Data
-- Demo Family: "Patil Family" owned by Parent Demo User (users.id = 7)
-- ====================================================================

USE reuniteai;

-- --------------------------------------------------------------------
-- 1. SEED FAMILIES
-- --------------------------------------------------------------------
INSERT INTO families (id, uuid, family_code, family_name, owner_user_id, primary_contact_name, primary_contact_mobile, emergency_contact_name, emergency_contact_mobile, preferred_language, status) VALUES
(1, 'fam-patil-001', 'RY-FAM-2026-000001', 'Patil Family', 7, 'Ramesh Chandra Swain', '9876543216', 'Amit Patil', '9988776655', 'or', 'ACTIVE');

-- Family Owner Access Record
INSERT INTO family_access (family_id, user_id, access_level, status) VALUES
(1, 7, 'OWNER', 'ACTIVE');

-- --------------------------------------------------------------------
-- 2. SEED PERSON PROFILES
-- --------------------------------------------------------------------
INSERT INTO person_profiles (id, uuid, person_code, full_name, date_of_birth, gender, age_category, height, approx_weight, hair_color, eye_color, skin_tone, identification_mark, glasses, hearing_aid, mobility_assistance, preferred_language, status) VALUES
(1, 'per-rajesh-001', 'RY-PER-2026-000001', 'Rajesh Patil', '1984-05-15', 'MALE', 'ADULT', '5ft 9in', '72 kg', 'Black', 'Brown', 'Wheatish', 'Mole on right forearm', 0, 0, 0, 'or', 'ACTIVE'),
(2, 'per-sneha-002', 'RY-PER-2026-000002', 'Sneha Patil', '1988-08-20', 'FEMALE', 'ADULT', '5ft 4in', '60 kg', 'Dark Brown', 'Brown', 'Fair', 'Small scar on chin', 0, 0, 0, 'or', 'ACTIVE'),
(3, 'per-aarav-003', 'RY-PER-2026-000003', 'Aarav Patil', '2018-03-10', 'MALE', 'CHILD', '4ft 1in', '26 kg', 'Black', 'Dark Brown', 'Fair', 'Birthmark on left shoulder', 0, 0, 0, 'or', 'ACTIVE'),
(4, 'per-sunita-004', 'RY-PER-2026-000004', 'Sunita Patil', '1959-11-04', 'FEMALE', 'ELDERLY', '5ft 1in', '55 kg', 'Grey/White', 'Brown', 'Wheatish', 'Surgical scar on right knee', 1, 1, 1, 'or', 'ACTIVE');

-- --------------------------------------------------------------------
-- 3. SEED FAMILY MEMBERS MAPPING
-- --------------------------------------------------------------------
INSERT INTO family_members (id, uuid, family_id, person_id, relationship_type, status) VALUES
(1, 'fm-001', 1, 1, 'Father', 'ACTIVE'),
(2, 'fm-002', 1, 2, 'Mother', 'ACTIVE'),
(3, 'fm-003', 1, 3, 'Son', 'ACTIVE'),
(4, 'fm-004', 1, 4, 'Grandmother', 'ACTIVE');

-- --------------------------------------------------------------------
-- 4. SEED CLOTHING PROFILES
-- --------------------------------------------------------------------
INSERT INTO clothing_profiles (person_id, top_type, top_color, bottom_type, bottom_color, footwear, footwear_color, headwear, accessories, description) VALUES
(1, 'Kurta', 'White', 'Pajama', 'White', 'Leather Sandals', 'Brown', 'None', 'Wrist Watch', 'Traditional pilgrim attire'),
(2, 'Saree', 'Yellow/Gold', 'Petticoat', 'Yellow', 'Chappals', 'Red', 'Dupatta', 'Gold Bangle', 'Silk festival saree'),
(3, 'T-Shirt', 'Bright Red', 'Shorts', 'Navy Blue', 'Sneakers', 'Blue', 'Cap', 'Yellow wristband', 'Spiderman logo red t-shirt'),
(4, 'Saree', 'Cotton Blue', 'Petticoat', 'Blue', 'Soft Orthopedic Shoes', 'Black', 'Shawl', 'Spectacles & Cane', 'Light blue cotton saree with walking stick');

-- --------------------------------------------------------------------
-- 5. SEED SAFETY PROFILES
-- --------------------------------------------------------------------
INSERT INTO person_safety_profiles (person_id, medical_condition, medication_requirement, allergy_information, blood_group, mobility_assistance, communication_difficulty, cognitive_assistance_required, consent_status) VALUES
(3, 'Mild Asthma', 'Inhaler in backpack', 'Dust allergy', 'O+', 'None', 'Speaks Odia/Hindi', 0, 1),
(4, 'Hypertension & Arthritis', 'Daily BP tablets morning/night', 'Penicillin allergy', 'B+', 'Uses walking stick', 'Hard of hearing in left ear', 1, 1);

-- --------------------------------------------------------------------
-- 6. SEED EMERGENCY CONTACTS
-- --------------------------------------------------------------------
INSERT INTO emergency_contacts (person_id, contact_name, relationship, mobile, alternate_mobile, is_primary) VALUES
(1, 'Amit Patil', 'Brother', '9988776655', '9988776654', 1),
(2, 'Rajesh Patil', 'Spouse', '9876543216', NULL, 1),
(3, 'Rajesh Patil', 'Father', '9876543216', '9988776655', 1),
(4, 'Rajesh Patil', 'Son', '9876543216', '9988776655', 1);

-- Seed Audit Log
INSERT INTO audit_logs (user_id, action, details, ip_address, user_agent, created_at) VALUES
(7, 'FAMILY_CREATED', 'Created family Patil Family (RY-FAM-2026-000001) with 4 pre-registered members', '127.0.0.1', 'System/Initializer', NOW());

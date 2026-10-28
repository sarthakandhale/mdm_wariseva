-- ====================================================================
-- WariSeva Platform - Module 5: Seed Data
-- Case Study: Alandi–Pandharpur Dindi Wari, Maharashtra
-- ====================================================================

USE reuniteai;

-- --------------------------------------------------------------------
-- 1. SEED FOUND PERSON CASES
-- --------------------------------------------------------------------
INSERT INTO found_person_cases (
    id, uuid, case_number, temporary_person_id, linked_person_id, reported_by_user_id, identification_status, approximate_name, approximate_age, gender, language, communication_status, medical_attention_required, special_assistance_required, dindi_id, status
) VALUES
(1, 'fp-001', 'WS-FP-2026-000001', 'TEMP-FP-PER-2026-00001', 3, 6, 'IDENTIFIED_PERSON', 'Aarav Patil', 8, 'MALE', 'Marathi', 'CAN_COMMUNICATE', 0, 'Rest & Water', NULL, 'VERIFICATION'),
(2, 'fp-002', 'WS-FP-2026-000002', 'TEMP-FP-PER-2026-00002', 4, 4, 'PARTIALLY_IDENTIFIED_PERSON', 'Sunita Patil', 67, 'FEMALE', 'Marathi', 'LIMITED_COMMUNICATION', 1, 'Medication check', NULL, 'FAMILY_CONTACTED'),
(3, 'fp-003', 'WS-FP-2026-000003', 'TEMP-FP-PER-2026-00003', NULL, 6, 'UNIDENTIFIED_PERSON', 'Unidentified Pilgrim', 65, 'MALE', 'Kannada', 'CANNOT_COMMUNICATE', 0, 'Interpreter & Wheelchair', NULL, 'REPORTED');

-- --------------------------------------------------------------------
-- 2. SEED FOUND PERSON LOCATIONS
-- --------------------------------------------------------------------
INSERT INTO found_person_locations (case_id, zone, route_section, landmark, latitude, longitude, location_description, location_source) VALUES
(1, 'Saswad', 'Alandi-Pandharpur Dindi Route', 'Saswad Help Center No. 2', 18.3460000, 74.0330000, 'Found sitting near Saswad Help Center 2', 'VOLUNTEER'),
(2, 'Jejuri', 'Alandi-Pandharpur Dindi Route', 'Jejuri Temple Arch', 18.2750000, 74.1580000, 'Spotted resting near temple gate by police patrol', 'POLICE'),
(3, 'Lonand', 'Alandi-Pandharpur Dindi Route', 'Lonand Palkhi Pavilion Stage 2', 18.0410000, 74.1910000, 'Found sitting alone near Annachhatra', 'VOLUNTEER');

-- --------------------------------------------------------------------
-- 3. SEED FOUND PERSON CLOTHING
-- --------------------------------------------------------------------
INSERT INTO found_person_clothing (case_id, top_type, top_color, bottom_type, bottom_color, footwear, footwear_color, headwear, accessories, description, confidence_level) VALUES
(1, 'T-Shirt', 'Red', 'Shorts', 'Navy Blue', 'Sneakers', 'Blue', 'Yellow Cap', 'Yellow Safety Wristband', 'Spiderman printed red shirt', 'HIGH'),
(2, 'Saree', 'Blue', 'Pajama', 'White', 'Sandals', 'Brown', 'Saree Pallu', 'Gold bangles', 'Cotton blue saree', 'HIGH'),
(3, 'Kurta', 'White', 'Pyjama', 'White', 'Slippers', 'Black', 'Gandhi Cap', 'Tulsi mala', 'Elderly pilgrim in traditional dhoti kurta', 'MEDIUM');

-- --------------------------------------------------------------------
-- 4. SEED SAFE LOCATIONS
-- --------------------------------------------------------------------
INSERT INTO found_person_safe_locations (case_id, facility_type, facility_id, location_name, status) VALUES
(1, 'HELP_CENTER', 2, 'Saswad Help Center No. 2', 'AT_HELP_CENTER'),
(2, 'POLICE_POST', 1, 'Jejuri Police Control Post 1', 'AT_POLICE_POST'),
(3, 'HELP_CENTER', 1, 'Lonand Help Center No. 1', 'AT_HELP_CENTER');

-- --------------------------------------------------------------------
-- 5. SEED IDENTIFICATION CLUES
-- --------------------------------------------------------------------
INSERT INTO found_person_identification_clues (case_id, clue_type, clue_value, source, confidence, verified) VALUES
(1, 'NAME', 'Aarav Patil', 'Verbal statement', 'HIGH', 1),
(1, 'DINDI_NUMBER', 'Dindi 27', 'Verbal statement', 'HIGH', 1),
(2, 'FAMILY_NAME', 'Patil Family of Pune', 'Verbal statement', 'MEDIUM', 0),
(3, 'VILLAGE', 'Belagavi Village', 'Verbal statement', 'LOW', 0);

-- --------------------------------------------------------------------
-- 6. SEED CASE NOTES
-- --------------------------------------------------------------------
INSERT INTO found_person_notes (case_id, created_by, note, visibility) VALUES
(1, 6, 'Aarav is safe and resting at Saswad Help Center 2. Biscuits and water provided.', 'FAMILY_VISIBLE'),
(2, 4, 'Sunita Patil resting at Jejuri Police Post. Family contact attempt in progress.', 'INTERNAL');

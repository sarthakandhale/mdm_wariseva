-- ====================================================================
-- WariSeva Platform - Module 4: Seed Data
-- Case Study: Alandi–Pandharpur Dindi Wari, Maharashtra
-- ====================================================================

USE reuniteai;

-- --------------------------------------------------------------------
-- 1. SEED LOST PERSON CASES
-- --------------------------------------------------------------------
INSERT INTO lost_person_cases (
    id, uuid, case_number, person_id, temp_person_code, temp_person_name, temp_person_age, temp_person_gender, temp_person_description,
    family_id, dindi_id, reported_by_user_id, reporter_relationship, reported_at, last_seen_at, priority_score, priority_level, priority_reasons, status, additional_information
) VALUES
(1, 'lp-001', 'WS-LP-2026-000001', 3, NULL, NULL, NULL, NULL, NULL, 1, NULL, 7, 'Father', NOW(), NOW(), 85, 'CRITICAL', 'Child under 12 (+30), Disappeared near crowded Palkhi halt (+10), Night-time (+10), Spiderman red shirt (+10), Known asthma (+25)', 'SEARCHING', 'Aarav went missing near Saswad Rest Stop Water Tank 3 during afternoon tea break.'),
(2, 'lp-002', 'WS-LP-2026-000002', 4, NULL, NULL, NULL, NULL, NULL, 1, NULL, 7, 'Son', NOW(), NOW(), 60, 'HIGH', 'Elderly 60+ (+25), Medical requirement hypertension (+25), Disappeared in crowd (+10)', 'REPORTED', 'Sunita Patil separated from group near Jejuri Temple steps.'),
(3, 'lp-003', 'WS-LP-2026-000003', NULL, 'TEMP-PER-2026-00001', 'Unregistered Boy', 6, 'MALE', 'Child in green t-shirt crying near Lonand Palkhi Pavilion', NULL, NULL, 6, 'Volunteer Report', NOW(), NOW(), 80, 'CRITICAL', 'Child under 12 (+30), Non-verbal (+20), Unregistered (+15), High density zone (+15)', 'UNDER_REVIEW', 'Child found wandering alone by volunteer team near Lonand.');

-- --------------------------------------------------------------------
-- 2. SEED LOST PERSON LOCATIONS
-- --------------------------------------------------------------------
INSERT INTO lost_person_locations (case_id, zone, route_section, landmark, latitude, longitude, location_description, location_source) VALUES
(1, 'Saswad', 'Alandi-Pandharpur Dindi Route', 'Saswad Rest Stop Water Tank 3', 18.3450000, 74.0320000, 'Behind Water Dispenser 3 near Palkhi Pavilion', 'MANUAL'),
(2, 'Jejuri', 'Alandi-Pandharpur Dindi Route', 'Jejuri Temple Main Steps', 18.2747000, 74.1578000, 'Near Deepastambha entrance', 'MANUAL'),
(3, 'Lonand', 'Alandi-Pandharpur Dindi Route', 'Lonand Palkhi Pavilion Stage 2', 18.0400000, 74.1900000, 'Near Annachhatra Distribution Center', 'VOLUNTEER');

-- --------------------------------------------------------------------
-- 3. SEED LOST PERSON CLOTHING
-- --------------------------------------------------------------------
INSERT INTO lost_person_clothing (case_id, top_type, top_color, bottom_type, bottom_color, footwear, footwear_color, headwear, accessories, description, confirmed_from_profile) VALUES
(1, 'T-Shirt', 'Bright Red with Spiderman', 'Shorts', 'Navy Blue', 'Sneakers', 'Blue', 'Yellow Cap', 'Yellow Safety Wristband', 'Carrying small blue backpack', 1),
(2, 'Saree', 'Cotton Blue', 'Pajama', 'White', 'Sandals', 'Brown', 'Saree Pallu', 'Gold bangles', 'Walking cane in hand', 1),
(3, 'T-Shirt', 'Green', 'Pants', 'Black', 'Slippers', 'Black', 'None', 'Red string on right wrist', 'Green printed t-shirt', 0);

-- --------------------------------------------------------------------
-- 4. SEED LOST PERSON NOTES
-- --------------------------------------------------------------------
INSERT INTO lost_person_notes (case_id, created_by, note, visibility) VALUES
(1, 7, 'Checked water tank area with volunteers. Moving toward Saswad Help Center No. 2.', 'FAMILY_VISIBLE'),
(1, 4, 'Help center announced missing report on loudspeaker in Zone 4.', 'INTERNAL');

-- --------------------------------------------------------------------
-- 5. SEED SEARCH REQUESTS
-- --------------------------------------------------------------------
INSERT INTO lost_person_search_requests (case_id, requested_by, zone, priority, description, status) VALUES
(1, 7, 'Saswad', 'CRITICAL', 'Volunteers requested to search Saswad Palkhi Halt Tent 4 and Food Distribution Area', 'REQUESTED');

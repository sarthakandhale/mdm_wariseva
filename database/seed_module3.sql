-- ====================================================================
-- WariSeva Platform - Module 3: Seed Data
-- Case Study: Alandi–Pandharpur Dindi Wari, Maharashtra
-- ====================================================================

USE reuniteai;

-- --------------------------------------------------------------------
-- 1. SEED MEDICAL FACILITIES
-- --------------------------------------------------------------------
INSERT INTO medical_facilities (id, uuid, facility_code, name, facility_type, zone, latitude, longitude, contact_number, capacity, current_patients, status) VALUES
(1, 'fac-001', 'WS-FAC-001', 'Alandi Temple First Aid Center', 'FIRST_AID_CENTER', 'Alandi', 18.6773000, 73.8967000, '02027180001', 60, 12, 'AVAILABLE'),
(2, 'fac-002', 'WS-FAC-002', 'Pune Wari Emergency Center', 'EMERGENCY_CENTER', 'Pune Route', 18.5204000, 73.8567000, '02026120002', 150, 45, 'AVAILABLE'),
(3, 'fac-003', 'WS-FAC-003', 'Saswad Wari Medical Camp 12', 'MEDICAL_CAMP', 'Saswad', 18.3444000, 74.0306000, '02115222003', 100, 72, 'AVAILABLE'),
(4, 'fac-004', 'WS-FAC-004', 'Jejuri Temple Health Booth', 'FIRST_AID_CENTER', 'Jejuri', 18.2747000, 74.1578000, '02115253004', 50, 48, 'BUSY'),
(5, 'fac-005', 'WS-FAC-005', 'Lonand Dindi Medical Base', 'MEDICAL_CAMP', 'Lonand', 18.0400000, 74.1900000, '02169224005', 80, 20, 'AVAILABLE'),
(6, 'fac-006', 'WS-FAC-006', 'Pandharpur Vitthal General Hospital', 'HOSPITAL', 'Pandharpur', 17.6775000, 75.3278000, '02186223006', 200, 110, 'AVAILABLE');

-- --------------------------------------------------------------------
-- 2. SEED FACILITY SERVICES
-- --------------------------------------------------------------------
INSERT INTO medical_facility_services (facility_id, service_name, available) VALUES
(1, 'First Aid', 1), (1, 'Dehydration Treatment', 1), (1, 'Wound Care', 1),
(2, 'Emergency Treatment', 1), (2, 'Cardiac Support', 1), (2, 'Ambulance Support', 1), (2, 'Pharmacy', 1),
(3, 'First Aid', 1), (3, 'Dehydration Treatment', 1), (3, 'Orthopedic Support', 1), (3, 'Pharmacy', 1),
(4, 'First Aid', 1), (4, 'Wound Care', 1),
(5, 'Dehydration Treatment', 1), (5, 'Orthopedic Support', 1), (5, 'First Aid', 1),
(6, 'Emergency Treatment', 1), (6, 'Cardiac Support', 1), (6, 'Orthopedic Support', 1), (6, 'Pharmacy', 1);

-- --------------------------------------------------------------------
-- 3. SEED MEDICAL STAFF
-- --------------------------------------------------------------------
INSERT INTO medical_staff (id, uuid, user_id, staff_code, staff_role, qualification, specialization, facility_id, shift_start, shift_end, status) VALUES
(1, 'stf-001', 5, 'WS-STF-001', 'DOCTOR', 'MBBS, MD', 'Emergency Medicine & Trauma', 3, '08:00', '20:00', 'ON_DUTY');

-- --------------------------------------------------------------------
-- 4. SEED AMBULANCES
-- --------------------------------------------------------------------
INSERT INTO ambulances (id, uuid, ambulance_code, registration_number, ambulance_type, driver_name, driver_contact, latitude, longitude, status, equipment_description) VALUES
(1, 'amb-101', 'WS-AMB-101', 'MH-12-PA-1001', 'ADVANCED_LIFE_SUPPORT', 'Santosh Pawar', '9822001122', 18.3450000, 74.0310000, 'AVAILABLE', 'Defibrillator, Oxygen Cylinder, Ventilator, Stretcher'),
(2, 'amb-102', 'WS-AMB-102', 'MH-12-PA-1002', 'BASIC_LIFE_SUPPORT', 'Ganesh Jadhav', '9822001123', 18.5210000, 73.8570000, 'AVAILABLE', 'First Aid Kit, Oxygen Mask, Stretcher'),
(3, 'amb-103', 'WS-AMB-103', 'MH-14-BT-2005', 'PATIENT_TRANSPORT', 'Anil Shinde', '9822001124', 18.0410000, 74.1910000, 'AVAILABLE', 'Basic First Aid & Stretcher');

-- --------------------------------------------------------------------
-- 5. SEED DEMO MEDICAL CASES
-- --------------------------------------------------------------------
INSERT INTO medical_cases (id, uuid, case_number, patient_person_id, temp_patient_code, temp_patient_name, temp_patient_age, temp_patient_gender, temp_patient_description, reported_by_user_id, emergency_type, reported_severity, priority_score, priority_level, priority_reasons, description, status, created_at) VALUES
(1, 'mc-001', 'WS-MED-2026-000001', 4, NULL, NULL, NULL, NULL, NULL, 7, 'BREATHING_DIFFICULTY', 'HIGH', 85, 'CRITICAL', 'Breathing difficulty (+35), Elderly patient (+15), Known hypertension (+20), High-risk route zone (+10)', 'Grandmother Sunita Patil experiencing breathing tightness near Saswad halt.', 'TRIAGE', NOW()),
(2, 'mc-002', 'WS-MED-2026-000002', 3, NULL, NULL, NULL, NULL, NULL, 7, 'DEHYDRATION', 'MEDIUM', 35, 'MEDIUM', 'Dehydration (+20), Child (+15)', 'Aarav Patil showing signs of fatigue and mild fever after long walking stretch.', 'REPORTED', NOW()),
(3, 'mc-003', 'WS-MED-2026-000003', NULL, 'TEMP-PAT-2026-00001', 'Unidentified Warkari', 55, 'MALE', 'Male warkari wearing white kurta and green turban found unconscious near Pargaon bridge.', 6, 'FAINTING', 'CRITICAL', 85, 'CRITICAL', 'Unconscious (+40), Severe fatigue (+20), High-risk route zone (+10), Unidentified (+15)', 'Unconscious pilgrim collapsed on road during afternoon heat.', 'ASSIGNED', NOW());

-- Location for Cases
INSERT INTO medical_case_locations (case_id, zone, route, landmark, latitude, longitude, location_description, location_source) VALUES
(1, 'Saswad', 'Alandi-Pandharpur Dindi Route', 'Near Saswad Palkhi Halt Tent 4', 18.3444000, 74.0306000, 'Behind Palkhi Pavilion', 'GPS'),
(2, 'Saswad', 'Alandi-Pandharpur Dindi Route', 'Saswad Rest Stop Kiosk', 18.3450000, 74.0320000, 'Near Water Dispenser 3', 'MANUAL'),
(3, 'Lonand', 'Pune-Pandharpur Highway', 'Pargaon Bridge Crossing', 18.0400000, 74.1900000, 'Right shoulder of main road', 'VOLUNTEER');

-- Symptoms for Cases
INSERT INTO medical_case_symptoms (case_id, symptom, severity) VALUES
(1, 'Difficulty breathing', 'HIGH'), (1, 'Chest tightness', 'HIGH'),
(2, 'Dizziness', 'MODERATE'), (2, 'Dehydration', 'MODERATE'),
(3, 'Unconsciousness', 'CRITICAL'), (3, 'Fever', 'HIGH');

-- Initial Audit Log Entry
INSERT INTO audit_logs (user_id, action, details, ip_address, user_agent, created_at) VALUES
(1, 'SYSTEM_INIT', 'WariSeva Module 3 initialized with Alandi-Pandharpur route medical camps, ambulances, and staff', '127.0.0.1', 'System/Initializer', NOW());

-- ====================================================================
-- WariSeva Platform - Module 6: Seed Data
-- Case Study: Alandi–Pandharpur Dindi Wari, Maharashtra
-- ====================================================================

USE reuniteai;

-- --------------------------------------------------------------------
-- 1. SEED STORAGE LOCATIONS
-- --------------------------------------------------------------------
INSERT INTO item_storage_locations (id, facility_name, facility_code, locker, shelf, capacity, current_count, status) VALUES
(1, 'Saswad Help Center Storage Tent 2', 'FAC-SAS-02', 'Locker B-12', 'Shelf 3', 50, 1, 'AVAILABLE'),
(2, 'Jejuri Police Post Locker Desk', 'FAC-JEJ-01', 'Cabinet A-04', 'Shelf 1', 30, 0, 'AVAILABLE');

-- --------------------------------------------------------------------
-- 2. SEED LOST ITEM CASES
-- --------------------------------------------------------------------
INSERT INTO lost_item_cases (
    id, uuid, case_number, reported_by_user_id, item_category, item_name, brand, model, color, description, approximate_value, serial_number, imei, status
) VALUES
(1, 'li-001', 'WS-LI-2026-000001', 7, 'MOBILE_PHONE', 'Samsung Galaxy A54', 'Samsung', 'Galaxy A54 5G', 'Black', 'Black phone in blue silicon cover with cracked screen guard', 25000.00, 'SN-SAMS-998811', '354892019283741', 'REPORTED'),
(2, 'li-002', 'WS-LI-2026-000002', 7, 'WALLET', 'Leather Brown Wallet', 'Titan', 'Classic', 'Brown', 'Leather wallet containing Aadhaar card and cash', 1500.00, NULL, NULL, 'REPORTED');

-- --------------------------------------------------------------------
-- 3. SEED FOUND ITEM CASES
-- --------------------------------------------------------------------
INSERT INTO found_item_cases (
    id, uuid, case_number, reported_by_user_id, item_category, item_name, brand, model, color, description, `condition`, found_by_user_id, status
) VALUES
(1, 'fi-001', 'WS-FI-2026-000001', 6, 'MOBILE_PHONE', 'Black Smartphone in Blue Cover', 'Samsung', 'Galaxy Series', 'Black', 'Found near Saswad halt water dispenser. Has blue cover.', 'GOOD', 6, 'STORED');

-- --------------------------------------------------------------------
-- 4. SEED LOCATIONS
-- --------------------------------------------------------------------
INSERT INTO item_locations (lost_item_case_id, found_item_case_id, zone, route_section, landmark, location_type, location_description) VALUES
(1, NULL, 'Saswad', 'Alandi-Pandharpur Dindi Route', 'Saswad Halt Water Dispenser 3', 'LOST', 'Dropped during tea halt near water dispenser'),
(NULL, 1, 'Saswad', 'Alandi-Pandharpur Dindi Route', 'Saswad Halt Water Dispenser 3', 'FOUND', 'Picked up near water tank by volunteer team');

-- --------------------------------------------------------------------
-- 5. SEED ITEM CLAIMS
-- --------------------------------------------------------------------
INSERT INTO item_claims (id, claim_number, found_item_case_id, claimed_by_user_id, claim_description, status) VALUES
(1, 'CLM-2026-000001', 1, 7, 'This is my Samsung Galaxy A54 phone. Wallpaper has picture of Vitthal temple.', 'SUBMITTED');

-- --------------------------------------------------------------------
-- 6. SEED CUSTODY HISTORY
-- --------------------------------------------------------------------
INSERT INTO item_custody_history (found_item_case_id, from_user_id, to_user_id, from_location, to_location, action, notes) VALUES
(1, 6, 6, 'Saswad Halt Water Dispenser 3', 'Saswad Help Center Storage Tent 2', 'STORED', 'Stored in Locker B-12 by volunteer team');

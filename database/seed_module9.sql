-- ====================================================================
-- WariSeva Platform - Module 9: Seed Data
-- Case Study: Alandi–Pandharpur Dindi Wari, Maharashtra
-- ====================================================================

USE reuniteai;

-- --------------------------------------------------------------------
-- 1. SEED WARI ROUTE
-- --------------------------------------------------------------------
INSERT INTO wari_routes (id, uuid, route_code, name, start_location, destination, total_distance, status) VALUES
(1, 'route-001', 'WS-ROUTE-2026-000001', 'Alandi–Pandharpur Palkhi Route', 'Alandi', 'Pandharpur', 242.50, 'ACTIVE');

-- --------------------------------------------------------------------
-- 2. SEED ROUTE SECTIONS
-- --------------------------------------------------------------------
INSERT INTO route_sections (id, route_id, section_code, sequence_number, start_location, end_location, distance_km, estimated_duration, status) VALUES
(1, 1, 'SEC-01', 1, 'Alandi', 'Pune', 22.00, '1 Day', 'ACTIVE'),
(2, 1, 'SEC-02', 2, 'Pune', 'Saswad', 32.00, '1 Day', 'ACTIVE'),
(3, 1, 'SEC-03', 3, 'Saswad', 'Jejuri', 16.00, '1 Day', 'ACTIVE'),
(4, 1, 'SEC-04', 4, 'Jejuri', 'Lonand', 22.00, '1 Day', 'ACTIVE'),
(5, 1, 'SEC-05', 5, 'Lonand', 'Phaltan', 32.00, '1 Day', 'ACTIVE'),
(6, 1, 'SEC-06', 6, 'Phaltan', 'Malshiras', 48.00, '2 Days', 'ACTIVE'),
(7, 1, 'SEC-07', 7, 'Malshiras', 'Pandharpur', 70.50, '2 Days', 'ACTIVE');

-- --------------------------------------------------------------------
-- 3. SEED WARI LOCATIONS / FACILITIES
-- --------------------------------------------------------------------
INSERT INTO wari_locations (id, uuid, name, location_type, route_section_id, zone, latitude, longitude, description, contact_number, status) VALUES
(1, 'loc-med-01', 'Saswad Route Medical Camp 1', 'MEDICAL_CAMP', 3, 'Saswad', 18.3450000, 74.0320000, '24/7 First-aid emergency medical tent near Saswad water station', '+91 98220 11111', 'OPEN'),
(2, 'loc-hc-01', 'Saswad Help Center Kiosk 2', 'HELP_CENTER', 3, 'Saswad', 18.3440000, 74.0310000, 'Kiosk desk for lost person & item inquiries', '+91 98220 22222', 'OPEN'),
(3, 'loc-rest-01', 'Saswad Water Dispenser & Rest Spot 3', 'WATER_POINT', 3, 'Saswad', 18.3460000, 74.0330000, 'Pilgrim drinking water dispensers and rest shade', '+91 98220 33333', 'OPEN'),
(4, 'loc-cp-01', 'Saswad Route Checkpoint 3', 'HELP_CENTER', 3, 'Saswad', 18.3455000, 74.0325000, 'Official Palkhi passage check-in desk', '+91 98220 44444', 'OPEN');

-- --------------------------------------------------------------------
-- 4. SEED CROWD ZONES
-- --------------------------------------------------------------------
INSERT INTO crowd_zones (id, zone_code, zone_name, route_section_id, crowd_level, updated_by) VALUES
(1, 'Z-SAS-01', 'Saswad Dive Ghat Ascent Zone', 2, 'MODERATE', 1);

-- --------------------------------------------------------------------
-- 5. SEED DINDI LOCATION UPDATES
-- --------------------------------------------------------------------
INSERT INTO dindi_location_updates (dindi_id, latitude, longitude, accuracy, location_source, status, recorded_by) VALUES
(1, 18.3450000, 74.0320000, 12.5, 'GPS', 'MOVING', 5);

-- --------------------------------------------------------------------
-- 6. SEED DINDI CHECKINS
-- --------------------------------------------------------------------
INSERT INTO dindi_checkins (dindi_id, checkpoint_id, checked_in_by, latitude, longitude, status) VALUES
(1, 4, 5, 18.3455000, 74.0325000, 'PASSED');

-- ====================================================================
-- WariSeva Platform - Module 9: Dindi Route, Location & Wari Movement Schema
-- Case Study: Alandi–Pandharpur Dindi Wari, Maharashtra
-- Database Target: MySQL 8.0+ (integrated with reuniteai DB)
-- ====================================================================

USE reuniteai;

-- --------------------------------------------------------------------
-- 1. WARI_ROUTES TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS wari_routes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    route_code VARCHAR(30) NOT NULL UNIQUE, -- e.g. WS-ROUTE-2026-000001
    name VARCHAR(150) NOT NULL,
    start_location VARCHAR(100) NOT NULL DEFAULT 'Alandi',
    destination VARCHAR(100) NOT NULL DEFAULT 'Pandharpur',
    total_distance DECIMAL(8, 2) DEFAULT 242.50,
    status ENUM('OPEN', 'ACTIVE', 'CLOSED') NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_wr_code (route_code),
    INDEX idx_wr_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 2. ROUTE_SECTIONS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS route_sections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    route_id INT NOT NULL,
    section_code VARCHAR(30) NOT NULL UNIQUE,
    sequence_number INT NOT NULL,
    start_location VARCHAR(100) NOT NULL,
    end_location VARCHAR(100) NOT NULL,
    distance_km DECIMAL(6, 2) NOT NULL,
    estimated_duration VARCHAR(50) DEFAULT '1 Day',
    status ENUM('OPEN', 'ACTIVE', 'CONGESTED', 'RESTRICTED', 'CLOSED', 'DETOUR') NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (route_id) REFERENCES wari_routes(id) ON DELETE CASCADE,
    INDEX idx_rs_sequence (sequence_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 3. ROUTE_POINTS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS route_points (
    id INT AUTO_INCREMENT PRIMARY KEY,
    route_section_id INT NOT NULL,
    sequence_number INT NOT NULL,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    point_name VARCHAR(150) NULL,
    point_type ENUM('WAYPOINT', 'CHECKPOINT', 'REST_SPOT') NOT NULL DEFAULT 'WAYPOINT',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (route_section_id) REFERENCES route_sections(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 4. WARI_LOCATIONS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS wari_locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    location_type ENUM(
        'START_POINT', 'DESTINATION', 'REST_POINT', 'WATER_POINT', 'FOOD_POINT',
        'MEDICAL_CAMP', 'HOSPITAL', 'HELP_CENTER', 'POLICE_POST', 'TOILET',
        'PARKING', 'DINDI_CAMP', 'EMERGENCY_POINT', 'OTHER'
    ) NOT NULL DEFAULT 'OTHER',
    route_section_id INT NULL,
    zone VARCHAR(50) NOT NULL,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    description TEXT NULL,
    contact_number VARCHAR(30) NULL,
    status ENUM('OPEN', 'CLOSED', 'BUSY', 'FULL', 'TEMPORARILY_CLOSED', 'EMERGENCY_ONLY', 'UNKNOWN') NOT NULL DEFAULT 'OPEN',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (route_section_id) REFERENCES route_sections(id) ON DELETE SET NULL,
    INDEX idx_wl_type (location_type),
    INDEX idx_wl_zone (zone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 5. DINDI_LOCATION_UPDATES TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dindi_location_updates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dindi_id INT NOT NULL,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    accuracy REAL DEFAULT 15.0,
    location_source ENUM('GPS', 'MANUAL', 'CHECKPOINT', 'LEADER', 'ADMIN') NOT NULL DEFAULT 'MANUAL',
    status ENUM('ACTIVE', 'MOVING', 'RESTING', 'DELAYED', 'STOPPED', 'UNKNOWN') NOT NULL DEFAULT 'MOVING',
    recorded_by INT NOT NULL, -- FK to users.id
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dindi_id) REFERENCES dindis(id) ON DELETE CASCADE,
    FOREIGN KEY (recorded_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_dlu_dindi (dindi_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 6. DINDI_CHECKINS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dindi_checkins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dindi_id INT NOT NULL,
    checkpoint_id INT NOT NULL, -- FK to wari_locations.id
    checked_in_by INT NOT NULL, -- FK to users.id
    latitude DECIMAL(10, 7) NULL,
    longitude DECIMAL(10, 7) NULL,
    checked_in_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('PASSED', 'DELAYED', 'HALTED') NOT NULL DEFAULT 'PASSED',
    FOREIGN KEY (dindi_id) REFERENCES dindis(id) ON DELETE CASCADE,
    FOREIGN KEY (checkpoint_id) REFERENCES wari_locations(id) ON DELETE CASCADE,
    FOREIGN KEY (checked_in_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 7. ROUTE_ALERTS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS route_alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    route_section_id INT NULL,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    priority ENUM('NORMAL', 'IMPORTANT', 'URGENT') NOT NULL DEFAULT 'NORMAL',
    created_by INT NOT NULL, -- FK to users.id
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expiry_at TIMESTAMP NULL,
    status ENUM('ACTIVE', 'EXPIRED', 'CANCELLED') NOT NULL DEFAULT 'ACTIVE',
    FOREIGN KEY (route_section_id) REFERENCES route_sections(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 8. CROWD_ZONES TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS crowd_zones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    zone_code VARCHAR(30) NOT NULL UNIQUE,
    zone_name VARCHAR(100) NOT NULL,
    route_section_id INT NULL,
    crowd_level ENUM('LOW', 'MODERATE', 'HIGH', 'SEVERE') NOT NULL DEFAULT 'LOW',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT NOT NULL,
    FOREIGN KEY (route_section_id) REFERENCES route_sections(id) ON DELETE CASCADE,
    FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 9. EMERGENCY_ZONES TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS emergency_zones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    zone_code VARCHAR(30) NOT NULL UNIQUE,
    route_section_id INT NULL,
    reason VARCHAR(255) NOT NULL,
    priority ENUM('HIGH', 'URGENT') NOT NULL DEFAULT 'HIGH',
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    active_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active_until TIMESTAMP NULL,
    status ENUM('ACTIVE', 'RESOLVED') NOT NULL DEFAULT 'ACTIVE',
    created_by INT NOT NULL,
    FOREIGN KEY (route_section_id) REFERENCES route_sections(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

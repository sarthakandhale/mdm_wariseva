-- ====================================================================
-- WariSeva Platform - Module 4: Lost Person Assistance & Missing Case Management Schema
-- Case Study: Alandi–Pandharpur Dindi Wari, Maharashtra
-- Database Target: MySQL 8.0+ (integrated with reuniteai DB)
-- ====================================================================

USE reuniteai;

-- --------------------------------------------------------------------
-- 1. LOST_PERSON_CASES TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS lost_person_cases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    case_number VARCHAR(30) NOT NULL UNIQUE, -- e.g. WS-LP-2026-000001
    person_id INT NULL, -- FK to person_profiles.id (NULL if temporary unidentified profile)
    temp_person_code VARCHAR(30) NULL, -- e.g. TEMP-PER-2026-00001
    temp_person_name VARCHAR(100) NULL,
    temp_person_age INT NULL,
    temp_person_gender VARCHAR(10) NULL,
    temp_person_description TEXT NULL,
    family_id INT NULL, -- FK to families.id
    dindi_id INT NULL, -- FK placeholder for Module 8 Dindi Management
    reported_by_user_id INT NOT NULL, -- FK to users.id
    reporter_relationship VARCHAR(50) NOT NULL,
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP NOT NULL,
    priority_score INT NOT NULL DEFAULT 0,
    priority_level ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') NOT NULL DEFAULT 'LOW',
    priority_reasons TEXT NULL,
    is_priority_overridden TINYINT(1) DEFAULT 0,
    override_reason VARCHAR(255) NULL,
    overridden_by INT NULL, -- FK to users.id
    overridden_at TIMESTAMP NULL,
    status ENUM(
        'DRAFT', 'REPORTED', 'UNDER_REVIEW', 'SEARCHING',
        'POSSIBLE_SIGHTING', 'POSSIBLE_MATCH', 'VERIFICATION',
        'FOUND', 'REUNITED', 'WITHDRAWN', 'CLOSED'
    ) NOT NULL DEFAULT 'REPORTED',
    additional_information TEXT NULL,
    medical_attention_required TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    closed_at TIMESTAMP NULL,
    FOREIGN KEY (person_id) REFERENCES person_profiles(id) ON DELETE SET NULL,
    FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE SET NULL,
    FOREIGN KEY (reported_by_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (overridden_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_lp_case_number (case_number),
    INDEX idx_lp_person (person_id),
    INDEX idx_lp_family (family_id),
    INDEX idx_lp_priority (priority_level),
    INDEX idx_lp_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 2. LOST_PERSON_LOCATIONS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS lost_person_locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    zone VARCHAR(50) NOT NULL, -- Alandi, Pune, Saswad, Jejuri, Lonand, Phaltan, Malshiras, Pandharpur
    route_section VARCHAR(100) NULL,
    landmark VARCHAR(150) NULL,
    dindi_id INT NULL,
    latitude DECIMAL(10, 7) NULL,
    longitude DECIMAL(10, 7) NULL,
    location_description TEXT NULL,
    location_source ENUM('GPS', 'MAP', 'MANUAL', 'DINDI_LEADER', 'POLICE', 'HELP_CENTER') DEFAULT 'MANUAL',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES lost_person_cases(id) ON DELETE CASCADE,
    INDEX idx_lp_loc_zone (zone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 3. LOST_PERSON_CLOTHING TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS lost_person_clothing (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    top_type VARCHAR(50) NULL,
    top_color VARCHAR(50) NULL,
    bottom_type VARCHAR(50) NULL,
    bottom_color VARCHAR(50) NULL,
    footwear VARCHAR(50) NULL,
    footwear_color VARCHAR(50) NULL,
    headwear VARCHAR(50) NULL,
    accessories VARCHAR(100) NULL,
    description TEXT NULL,
    confirmed_from_profile TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES lost_person_cases(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 4. LOST_PERSON_STATUS_HISTORY TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS lost_person_status_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    old_status VARCHAR(30) NULL,
    new_status VARCHAR(30) NOT NULL,
    changed_by INT NOT NULL,
    reason VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES lost_person_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 5. LOST_PERSON_ATTACHMENTS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS lost_person_attachments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    uploaded_by INT NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    file_name VARCHAR(150) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size INT NOT NULL,
    description VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES lost_person_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 6. LOST_PERSON_NOTES TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS lost_person_notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    created_by INT NOT NULL,
    note TEXT NOT NULL,
    visibility ENUM('INTERNAL', 'FAMILY_VISIBLE') NOT NULL DEFAULT 'FAMILY_VISIBLE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES lost_person_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 7. LOST_PERSON_SEARCH_REQUESTS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS lost_person_search_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    requested_by INT NOT NULL,
    zone VARCHAR(50) NOT NULL,
    priority VARCHAR(20) NOT NULL DEFAULT 'HIGH',
    description TEXT NULL,
    status ENUM('REQUESTED', 'ACCEPTED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED') NOT NULL DEFAULT 'REQUESTED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES lost_person_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (requested_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 8. LOST_PERSON_SIGHTINGS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS lost_person_sightings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    reported_by INT NOT NULL,
    location_description TEXT NOT NULL,
    zone VARCHAR(50) NOT NULL,
    latitude DECIMAL(10, 7) NULL,
    longitude DECIMAL(10, 7) NULL,
    sighting_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT NULL,
    photo_path VARCHAR(255) NULL,
    confidence_rating ENUM('LOW', 'MEDIUM', 'HIGH') DEFAULT 'MEDIUM',
    status ENUM('REPORTED', 'UNDER_REVIEW', 'CONFIRMED', 'REJECTED') DEFAULT 'REPORTED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES lost_person_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (reported_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

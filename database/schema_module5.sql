-- ====================================================================
-- WariSeva Platform - Module 5: Found Person Assistance & Safe Custody Schema
-- Case Study: Alandi–Pandharpur Dindi Wari, Maharashtra
-- Database Target: MySQL 8.0+ (integrated with reuniteai DB)
-- ====================================================================

USE reuniteai;

-- --------------------------------------------------------------------
-- 1. FOUND_PERSON_CASES TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS found_person_cases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    case_number VARCHAR(30) NOT NULL UNIQUE, -- e.g. WS-FP-2026-000001
    temporary_person_id VARCHAR(30) NOT NULL UNIQUE, -- e.g. TEMP-FP-PER-2026-00001
    linked_person_id INT NULL, -- FK to person_profiles.id (NULL if unidentified)
    reported_by_user_id INT NOT NULL, -- FK to users.id
    identification_status ENUM('IDENTIFIED_PERSON', 'PARTIALLY_IDENTIFIED_PERSON', 'UNIDENTIFIED_PERSON') NOT NULL DEFAULT 'UNIDENTIFIED_PERSON',
    approximate_name VARCHAR(100) NULL,
    approximate_age INT NULL,
    gender VARCHAR(10) NULL,
    language VARCHAR(50) DEFAULT 'Marathi',
    communication_status ENUM('CAN_COMMUNICATE', 'LIMITED_COMMUNICATION', 'CANNOT_COMMUNICATE', 'UNKNOWN') NOT NULL DEFAULT 'CAN_COMMUNICATE',
    medical_attention_required TINYINT(1) DEFAULT 0,
    medical_case_id INT NULL, -- FK to medical_cases.id
    special_assistance_required VARCHAR(255) NULL,
    dindi_id INT NULL, -- FK placeholder for Module 8 Dindi Management
    status ENUM(
        'REPORTED', 'UNDER_REVIEW', 'IDENTITY_SEARCH',
        'POSSIBLE_MATCH', 'VERIFICATION', 'IDENTITY_CONFIRMED',
        'FAMILY_CONTACTED', 'REUNIFICATION_PENDING', 'REUNITED',
        'TRANSFERRED', 'UNRESOLVED', 'CLOSED'
    ) NOT NULL DEFAULT 'REPORTED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    closed_at TIMESTAMP NULL,
    FOREIGN KEY (linked_person_id) REFERENCES person_profiles(id) ON DELETE SET NULL,
    FOREIGN KEY (reported_by_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (medical_case_id) REFERENCES medical_cases(id) ON DELETE SET NULL,
    INDEX idx_fp_case_number (case_number),
    INDEX idx_fp_temp_id (temporary_person_id),
    INDEX idx_fp_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 2. FOUND_PERSON_LOCATIONS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS found_person_locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    zone VARCHAR(50) NOT NULL, -- Alandi, Pune, Saswad, Jejuri, Lonand, Phaltan, Malshiras, Pandharpur
    route_section VARCHAR(100) NULL,
    landmark VARCHAR(150) NULL,
    dindi_id INT NULL,
    latitude DECIMAL(10, 7) NULL,
    longitude DECIMAL(10, 7) NULL,
    location_description TEXT NULL,
    location_source ENUM('GPS', 'MAP', 'MANUAL', 'VOLUNTEER', 'POLICE', 'DINDI_LEADER', 'MEDICAL_CAMP') DEFAULT 'VOLUNTEER',
    found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES found_person_cases(id) ON DELETE CASCADE,
    INDEX idx_fp_loc_zone (zone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 3. FOUND_PERSON_CLOTHING TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS found_person_clothing (
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
    confidence_level ENUM('HIGH', 'MEDIUM', 'LOW') DEFAULT 'HIGH',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES found_person_cases(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 4. FOUND_PERSON_PHOTOS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS found_person_photos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    uploaded_by INT NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size INT NOT NULL,
    is_primary TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES found_person_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 5. FOUND_PERSON_IDENTIFICATION_CLUES TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS found_person_identification_clues (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    clue_type ENUM('NAME', 'DINDI_NUMBER', 'VILLAGE', 'FAMILY_NAME', 'MOBILE', 'GUARDIAN_NAME', 'COMPANION', 'OTHER') NOT NULL,
    clue_value VARCHAR(255) NOT NULL,
    source VARCHAR(100) DEFAULT 'Person verbal statement',
    confidence ENUM('HIGH', 'MEDIUM', 'LOW') DEFAULT 'MEDIUM',
    verified TINYINT(1) DEFAULT 0,
    verified_by INT NULL, -- FK to users.id
    verified_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES found_person_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 6. FOUND_PERSON_SAFE_LOCATIONS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS found_person_safe_locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    facility_type ENUM('HELP_CENTER', 'POLICE_POST', 'MEDICAL_CAMP', 'DINDI_CAMP', 'OTHER_AUTHORIZED_CENTER') NOT NULL DEFAULT 'HELP_CENTER',
    facility_id INT NULL,
    location_name VARCHAR(150) NOT NULL,
    arrival_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    departure_time TIMESTAMP NULL,
    status ENUM('NOT_YET_SAFE', 'IN_TRANSIT', 'AT_HELP_CENTER', 'AT_POLICE_POST', 'AT_MEDICAL_CAMP', 'WITH_DINDI', 'REUNITED', 'TRANSFERRED', 'CLOSED') NOT NULL DEFAULT 'AT_HELP_CENTER',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES found_person_cases(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 7. FOUND_PERSON_FAMILY_CONTACTS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS found_person_family_contacts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    contact_name VARCHAR(100) NOT NULL,
    contact_number VARCHAR(20) NOT NULL,
    relationship VARCHAR(50) NULL,
    contact_method VARCHAR(50) DEFAULT 'Phone Call',
    contacted_by INT NOT NULL,
    contacted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    result VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES found_person_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (contacted_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 8. FOUND_PERSON_VERIFICATIONS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS found_person_verifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    verification_status ENUM('NOT_STARTED', 'IN_PROGRESS', 'VERIFIED', 'REJECTED') NOT NULL DEFAULT 'NOT_STARTED',
    verification_method ENUM('DOCUMENT', 'PERSONAL_INFORMATION', 'FAMILY_CONFIRMATION', 'DINDI_CONFIRMATION', 'POLICE_VERIFICATION', 'OTHER') NOT NULL DEFAULT 'PERSONAL_INFORMATION',
    verified_by INT NOT NULL,
    verification_notes TEXT NULL,
    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES found_person_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 9. FOUND_PERSON_REUNIFICATIONS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS found_person_reunifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    reunited_with VARCHAR(150) NOT NULL,
    verified_by INT NOT NULL,
    reunification_location VARCHAR(150) NOT NULL,
    reunification_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verification_method VARCHAR(100) DEFAULT 'FAMILY_CONFIRMATION',
    notes TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES found_person_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 10. FOUND_PERSON_STATUS_HISTORY TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS found_person_status_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    old_status VARCHAR(30) NULL,
    new_status VARCHAR(30) NOT NULL,
    changed_by INT NOT NULL,
    reason VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES found_person_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 11. FOUND_PERSON_NOTES TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS found_person_notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    created_by INT NOT NULL,
    note TEXT NOT NULL,
    visibility ENUM('INTERNAL', 'FAMILY_VISIBLE') NOT NULL DEFAULT 'FAMILY_VISIBLE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES found_person_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

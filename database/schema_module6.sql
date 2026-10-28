-- ====================================================================
-- WariSeva Platform - Module 6: Lost & Found Item Assistance & Recovery Schema
-- Case Study: Alandi–Pandharpur Dindi Wari, Maharashtra
-- Database Target: MySQL 8.0+ (integrated with reuniteai DB)
-- ====================================================================

USE reuniteai;

-- --------------------------------------------------------------------
-- 1. LOST_ITEM_CASES TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS lost_item_cases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    case_number VARCHAR(30) NOT NULL UNIQUE, -- e.g. WS-LI-2026-000001
    reported_by_user_id INT NOT NULL, -- FK to users.id
    item_category ENUM(
        'ELECTRONICS', 'DOCUMENT', 'MOBILE_PHONE', 'WALLET', 'BAG',
        'JEWELLERY', 'CLOTHING', 'FOOTWEAR', 'KEYS', 'EYEWEAR',
        'MONEY', 'MEDICAL_ITEM', 'IDENTIFICATION_CARD', 'OTHER'
    ) NOT NULL DEFAULT 'OTHER',
    item_name VARCHAR(100) NOT NULL,
    brand VARCHAR(50) NULL,
    model VARCHAR(50) NULL,
    color VARCHAR(50) NULL,
    description TEXT NULL,
    approximate_value DECIMAL(10, 2) DEFAULT 0.00,
    serial_number VARCHAR(100) NULL, -- Sensitive restricted field
    imei VARCHAR(50) NULL, -- Sensitive restricted field
    status ENUM(
        'REPORTED', 'UNDER_REVIEW', 'SEARCHING', 'POTENTIAL_MATCH',
        'CLAIMED', 'VERIFICATION', 'RETURNED', 'CLOSED', 'WITHDRAWN', 'UNRESOLVED'
    ) NOT NULL DEFAULT 'REPORTED',
    dindi_id INT NULL, -- FK placeholder for Module 8 Dindi Management
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    closed_at TIMESTAMP NULL,
    FOREIGN KEY (reported_by_user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_li_case_number (case_number),
    INDEX idx_li_category (item_category),
    INDEX idx_li_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 2. FOUND_ITEM_CASES TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS found_item_cases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    case_number VARCHAR(30) NOT NULL UNIQUE, -- e.g. WS-FI-2026-000001
    reported_by_user_id INT NOT NULL, -- FK to users.id
    item_category ENUM(
        'ELECTRONICS', 'DOCUMENT', 'MOBILE_PHONE', 'WALLET', 'BAG',
        'JEWELLERY', 'CLOTHING', 'FOOTWEAR', 'KEYS', 'EYEWEAR',
        'MONEY', 'MEDICAL_ITEM', 'IDENTIFICATION_CARD', 'OTHER'
    ) NOT NULL DEFAULT 'OTHER',
    item_name VARCHAR(100) NOT NULL,
    brand VARCHAR(50) NULL,
    model VARCHAR(50) NULL,
    color VARCHAR(50) NULL,
    description TEXT NULL,
    `condition` ENUM('NEW', 'GOOD', 'DAMAGED', 'HEAVILY_DAMAGED', 'BROKEN', 'UNKNOWN') NOT NULL DEFAULT 'GOOD',
    dindi_id INT NULL,
    found_by_user_id INT NOT NULL, -- FK to users.id
    status ENUM(
        'REPORTED', 'UNDER_REVIEW', 'STORED', 'POTENTIAL_MATCH',
        'CLAIM_PENDING', 'VERIFICATION', 'RETURNED', 'TRANSFERRED', 'UNCLAIMED', 'CLOSED'
    ) NOT NULL DEFAULT 'REPORTED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    closed_at TIMESTAMP NULL,
    FOREIGN KEY (reported_by_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (found_by_user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_fi_case_number (case_number),
    INDEX idx_fi_category (item_category),
    INDEX idx_fi_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 3. ITEM_PHOTOS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS item_photos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lost_item_case_id INT NULL,
    found_item_case_id INT NULL,
    uploaded_by INT NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size INT NOT NULL,
    is_primary TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lost_item_case_id) REFERENCES lost_item_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (found_item_case_id) REFERENCES found_item_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 4. ITEM_LOCATIONS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS item_locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lost_item_case_id INT NULL,
    found_item_case_id INT NULL,
    zone VARCHAR(50) NOT NULL,
    route_section VARCHAR(100) NULL,
    landmark VARCHAR(150) NULL,
    latitude DECIMAL(10, 7) NULL,
    longitude DECIMAL(10, 7) NULL,
    location_type ENUM('LOST', 'FOUND', 'STORAGE', 'TRANSFER', 'RETURN') NOT NULL DEFAULT 'LOST',
    location_description TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lost_item_case_id) REFERENCES lost_item_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (found_item_case_id) REFERENCES found_item_cases(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 5. ITEM_IDENTIFIERS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS item_identifiers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lost_item_case_id INT NULL,
    found_item_case_id INT NULL,
    identifier_type ENUM('SERIAL_NUMBER', 'IMEI', 'ID_NUMBER', 'UNIQUE_MARK') NOT NULL,
    identifier_value VARCHAR(255) NOT NULL,
    visibility ENUM('PRIVATE', 'AUTHORIZED_ONLY') NOT NULL DEFAULT 'AUTHORIZED_ONLY',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lost_item_case_id) REFERENCES lost_item_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (found_item_case_id) REFERENCES found_item_cases(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 6. ITEM_CLAIMS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS item_claims (
    id INT AUTO_INCREMENT PRIMARY KEY,
    claim_number VARCHAR(30) NOT NULL UNIQUE, -- e.g. CLM-2026-000001
    found_item_case_id INT NOT NULL,
    claimed_by_user_id INT NOT NULL,
    claim_description TEXT NOT NULL,
    status ENUM('SUBMITTED', 'UNDER_REVIEW', 'MORE_INFORMATION_REQUIRED', 'APPROVED', 'REJECTED', 'CANCELLED') NOT NULL DEFAULT 'SUBMITTED',
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    reviewed_by INT NULL,
    reviewed_at TIMESTAMP NULL,
    FOREIGN KEY (found_item_case_id) REFERENCES found_item_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (claimed_by_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_ic_claim_number (claim_number),
    INDEX idx_ic_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 7. ITEM_CLAIM_VERIFICATIONS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS item_claim_verifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    claim_id INT NOT NULL,
    verification_type ENUM('DESCRIPTION', 'PHOTO', 'SERIAL_NUMBER', 'PURCHASE_PROOF', 'UNIQUE_MARK', 'OTHER') NOT NULL,
    verification_result ENUM('MATCH', 'NO_MATCH', 'INCONCLUSIVE') NOT NULL DEFAULT 'MATCH',
    verification_notes TEXT NULL,
    verified_by INT NOT NULL,
    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (claim_id) REFERENCES item_claims(id) ON DELETE CASCADE,
    FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 8. ITEM_STORAGE_LOCATIONS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS item_storage_locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    facility_name VARCHAR(150) NOT NULL,
    facility_code VARCHAR(30) NOT NULL UNIQUE,
    locker VARCHAR(50) NOT NULL,
    shelf VARCHAR(50) NULL,
    capacity INT DEFAULT 50,
    current_count INT DEFAULT 0,
    status ENUM('AVAILABLE', 'FULL', 'CLOSED') NOT NULL DEFAULT 'AVAILABLE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 9. ITEM_CUSTODY_HISTORY TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS item_custody_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    found_item_case_id INT NOT NULL,
    from_user_id INT NULL,
    to_user_id INT NOT NULL,
    from_location VARCHAR(150) NULL,
    to_location VARCHAR(150) NOT NULL,
    action ENUM('RECEIVED', 'STORED', 'TRANSFERRED', 'RELEASED') NOT NULL DEFAULT 'RECEIVED',
    notes TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (found_item_case_id) REFERENCES found_item_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (from_user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (to_user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 10. ITEM_STATUS_HISTORY TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS item_status_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lost_item_case_id INT NULL,
    found_item_case_id INT NULL,
    old_status VARCHAR(30) NULL,
    new_status VARCHAR(30) NOT NULL,
    changed_by INT NOT NULL,
    reason VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lost_item_case_id) REFERENCES lost_item_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (found_item_case_id) REFERENCES found_item_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 11. ITEM_NOTES TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS item_notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lost_item_case_id INT NULL,
    found_item_case_id INT NULL,
    created_by INT NOT NULL,
    note TEXT NOT NULL,
    visibility ENUM('INTERNAL', 'USER_VISIBLE') NOT NULL DEFAULT 'USER_VISIBLE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (lost_item_case_id) REFERENCES lost_item_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (found_item_case_id) REFERENCES found_item_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 12. ITEM_MATCHES TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS item_matches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lost_item_case_id INT NOT NULL,
    found_item_case_id INT NOT NULL,
    match_type ENUM('MANUAL', 'AI') NOT NULL DEFAULT 'MANUAL',
    match_score INT DEFAULT 100,
    match_reason TEXT NULL,
    created_by INT NOT NULL,
    status ENUM('MANUAL_POTENTIAL_MATCH', 'APPROVED', 'REJECTED') NOT NULL DEFAULT 'MANUAL_POTENTIAL_MATCH',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lost_item_case_id) REFERENCES lost_item_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (found_item_case_id) REFERENCES found_item_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

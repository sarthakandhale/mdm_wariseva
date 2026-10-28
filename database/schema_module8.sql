-- ====================================================================
-- WariSeva Platform - Module 8: Dindi Management & Warkari Group Coordination Schema
-- Case Study: Alandi–Pandharpur Dindi Wari, Maharashtra
-- Database Target: MySQL 8.0+ (integrated with reuniteai DB)
-- ====================================================================

USE reuniteai;

-- --------------------------------------------------------------------
-- 1. DINDIS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dindis (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    dindi_code VARCHAR(30) NOT NULL UNIQUE, -- e.g. WS-DIN-2026-000027
    dindi_number INT NOT NULL UNIQUE, -- Display number e.g. 27
    name VARCHAR(150) NOT NULL,
    description TEXT NULL,
    registration_year INT DEFAULT 2026,
    start_location VARCHAR(100) DEFAULT 'Alandi',
    destination VARCHAR(100) DEFAULT 'Pandharpur',
    expected_member_count INT DEFAULT 100,
    status ENUM(
        'PENDING', 'VERIFIED', 'ACTIVE', 'PAUSED',
        'INACTIVE', 'COMPLETED', 'SUSPENDED'
    ) NOT NULL DEFAULT 'PENDING',
    created_by INT NOT NULL, -- FK to users.id
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_dindi_code (dindi_code),
    INDEX idx_dindi_number (dindi_number),
    INDEX idx_dindi_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 2. DINDI_LEADERS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dindi_leaders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dindi_id INT NOT NULL,
    person_id INT NULL, -- FK to person_profiles.id
    user_id INT NOT NULL, -- FK to users.id
    role ENUM('PRIMARY_LEADER', 'ASSISTANT_LEADER') NOT NULL DEFAULT 'PRIMARY_LEADER',
    start_date DATE NULL,
    end_date DATE NULL,
    status ENUM('ACTIVE', 'INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (dindi_id) REFERENCES dindis(id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES person_profiles(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 3. DINDI_MEMBERSHIPS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dindi_memberships (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dindi_id INT NOT NULL,
    person_id INT NOT NULL, -- FK to person_profiles.id
    membership_number VARCHAR(50) NULL,
    role ENUM('LEADER', 'ASSISTANT_LEADER', 'MEMBER', 'VOLUNTEER') NOT NULL DEFAULT 'MEMBER',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    left_at TIMESTAMP NULL,
    status ENUM('ACTIVE', 'INACTIVE', 'LEFT_DINDI', 'TRANSFERRED', 'TEMPORARY', 'SUSPENDED') NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (dindi_id) REFERENCES dindis(id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES person_profiles(id) ON DELETE CASCADE,
    UNIQUE KEY uk_dindi_person (dindi_id, person_id),
    INDEX idx_dm_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 4. DINDI_SCHEDULES TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dindi_schedules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dindi_id INT NOT NULL,
    schedule_date DATE NOT NULL,
    start_location VARCHAR(100) NOT NULL,
    end_location VARCHAR(100) NOT NULL,
    expected_start_time VARCHAR(20) DEFAULT '05:30 AM',
    expected_arrival_time VARCHAR(20) DEFAULT '06:00 PM',
    rest_point VARCHAR(150) NULL,
    notes TEXT NULL,
    status ENUM('SCHEDULED', 'COMPLETED', 'CANCELLED') NOT NULL DEFAULT 'SCHEDULED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (dindi_id) REFERENCES dindis(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 5. DINDI_ANNOUNCEMENTS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dindi_announcements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dindi_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    priority ENUM('NORMAL', 'IMPORTANT', 'URGENT') NOT NULL DEFAULT 'NORMAL',
    created_by INT NOT NULL, -- FK to users.id
    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expiry_at TIMESTAMP NULL,
    status ENUM('ACTIVE', 'EXPIRED', 'CANCELLED') NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (dindi_id) REFERENCES dindis(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 6. DINDI_CONTACTS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dindi_contacts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dindi_id INT NOT NULL,
    contact_type ENUM('PRIMARY', 'EMERGENCY', 'OFFICE', 'OTHER') NOT NULL DEFAULT 'PRIMARY',
    contact_name VARCHAR(100) NOT NULL,
    contact_number VARCHAR(30) NOT NULL,
    visibility ENUM('PUBLIC', 'LEADER_ONLY', 'ADMIN_ONLY') NOT NULL DEFAULT 'PUBLIC',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (dindi_id) REFERENCES dindis(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 7. DINDI_VERIFICATIONS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dindi_verifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dindi_id INT NOT NULL,
    status ENUM('PENDING', 'VERIFIED', 'REJECTED', 'REQUIRES_UPDATE') NOT NULL DEFAULT 'VERIFIED',
    verified_by INT NOT NULL, -- FK to users.id
    verification_notes TEXT NULL,
    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dindi_id) REFERENCES dindis(id) ON DELETE CASCADE,
    FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 8. DINDI_DOCUMENTS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dindi_documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dindi_id INT NOT NULL,
    uploaded_by INT NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    file_name VARCHAR(150) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dindi_id) REFERENCES dindis(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 9. DINDI_ROUTE_ASSOCIATIONS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dindi_route_associations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dindi_id INT NOT NULL,
    route_id INT DEFAULT 101, -- Connects to Module 9
    sequence_number INT DEFAULT 1,
    start_date DATE NULL,
    end_date DATE NULL,
    status ENUM('ACTIVE', 'COMPLETED', 'CANCELLED') NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (dindi_id) REFERENCES dindis(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

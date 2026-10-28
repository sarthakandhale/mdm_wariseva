-- ====================================================================
-- ReuniteAI Platform - Module 2: Family & Person Profile Management Schema
-- Database Target: MySQL 8.0+
-- Integrated with Module 1 Database (reuniteai)
-- ====================================================================

USE reuniteai;

-- --------------------------------------------------------------------
-- 1. FAMILIES TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS families (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    family_code VARCHAR(30) NOT NULL UNIQUE, -- e.g. RY-FAM-2026-000001
    family_name VARCHAR(100) NOT NULL,
    owner_user_id INT NOT NULL,
    primary_contact_name VARCHAR(100) NOT NULL,
    primary_contact_mobile VARCHAR(15) NOT NULL,
    emergency_contact_name VARCHAR(100) NOT NULL,
    emergency_contact_mobile VARCHAR(15) NOT NULL,
    preferred_language VARCHAR(10) DEFAULT 'en',
    notes TEXT NULL,
    status ENUM('ACTIVE', 'INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_family_owner (owner_user_id),
    INDEX idx_family_code (family_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 2. PERSON_PROFILES TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS person_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    person_code VARCHAR(30) NOT NULL UNIQUE, -- e.g. RY-PER-2026-000001
    full_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender ENUM('MALE', 'FEMALE', 'OTHER') NOT NULL,
    age_category ENUM('CHILD', 'MINOR', 'ADULT', 'ELDERLY') NOT NULL,
    height VARCHAR(20) NULL,
    approx_weight VARCHAR(20) NULL,
    hair_color VARCHAR(30) NULL,
    eye_color VARCHAR(30) NULL,
    skin_tone VARCHAR(30) NULL,
    identification_mark TEXT NULL,
    glasses TINYINT(1) DEFAULT 0,
    hearing_aid TINYINT(1) DEFAULT 0,
    walking_assistance TINYINT(1) DEFAULT 0,
    preferred_language VARCHAR(10) DEFAULT 'en',
    profile_visibility ENUM('PRIVATE', 'RESTRICTED', 'PUBLIC') DEFAULT 'PRIVATE',
    status ENUM('ACTIVE', 'INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_person_code (person_code),
    INDEX idx_person_age_cat (age_category),
    INDEX idx_person_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 3. FAMILY_MEMBERS TABLE (Many-to-Many Family to Person Mapping)
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS family_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    family_id INT NOT NULL,
    person_id INT NOT NULL,
    relationship_type VARCHAR(50) NOT NULL, -- Father, Mother, Son, Daughter, Travel Companion, etc.
    status ENUM('ACTIVE', 'INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES person_profiles(id) ON DELETE CASCADE,
    UNIQUE KEY idx_unique_family_person (family_id, person_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 4. PERSON_PHOTOS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS person_photos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    person_id INT NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    file_type VARCHAR(20) NOT NULL,
    file_size INT NOT NULL,
    is_primary TINYINT(1) DEFAULT 1,
    uploaded_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES person_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 5. CLOTHING_PROFILES TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clothing_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    person_id INT NOT NULL UNIQUE,
    top_type VARCHAR(50) NULL,
    top_color VARCHAR(30) NULL,
    bottom_type VARCHAR(50) NULL,
    bottom_color VARCHAR(30) NULL,
    footwear VARCHAR(50) NULL,
    footwear_color VARCHAR(30) NULL,
    headwear VARCHAR(50) NULL,
    accessories TEXT NULL,
    description TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES person_profiles(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 6. PERSON_SAFETY_PROFILES TABLE (Sensitive Medical Info)
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS person_safety_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    person_id INT NOT NULL UNIQUE,
    medical_condition TEXT NULL,
    medication_requirement TEXT NULL,
    allergy_information TEXT NULL,
    blood_group VARCHAR(10) NULL,
    mobility_assistance VARCHAR(100) NULL,
    communication_difficulty VARCHAR(100) NULL,
    cognitive_assistance_required TINYINT(1) DEFAULT 0,
    consent_status TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES person_profiles(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 7. EMERGENCY_CONTACTS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS emergency_contacts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    person_id INT NOT NULL,
    contact_name VARCHAR(100) NOT NULL,
    relationship VARCHAR(50) NOT NULL,
    mobile VARCHAR(15) NOT NULL,
    alternate_mobile VARCHAR(15) NULL,
    is_primary TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES person_profiles(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 8. FAMILY_ACCESS TABLE (Multiple Guardians Support)
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS family_access (
    id INT AUTO_INCREMENT PRIMARY KEY,
    family_id INT NOT NULL,
    user_id INT NOT NULL,
    access_level ENUM('OWNER', 'EDITOR', 'VIEWER') NOT NULL DEFAULT 'VIEWER',
    status ENUM('ACTIVE', 'REVOKED') NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY idx_unique_family_user_access (family_id, user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

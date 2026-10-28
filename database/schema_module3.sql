-- ====================================================================
-- WariSeva Platform - Module 3: Medical Emergency Assistance Schema
-- Case Study: Alandi–Pandharpur Dindi Wari, Maharashtra
-- Database Target: MySQL 8.0+ (integrated with reuniteai DB)
-- ====================================================================

USE reuniteai;

-- --------------------------------------------------------------------
-- 1. MEDICAL_CASES TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS medical_cases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    case_number VARCHAR(30) NOT NULL UNIQUE, -- e.g. WS-MED-2026-000001
    patient_person_id INT NULL, -- FK to person_profiles (NULL if unidentified temporary patient)
    temp_patient_code VARCHAR(30) NULL, -- e.g. TEMP-PAT-2026-00001
    temp_patient_name VARCHAR(100) NULL,
    temp_patient_age INT NULL,
    temp_patient_gender VARCHAR(10) NULL,
    temp_patient_description TEXT NULL,
    reported_by_user_id INT NOT NULL, -- FK to users.id
    emergency_type ENUM(
        'INJURY', 'ACCIDENT', 'DEHYDRATION', 'HEAT_EXHAUSTION', 'FAINTING',
        'BREATHING_DIFFICULTY', 'CHEST_PAIN', 'ALLERGIC_REACTION', 'MEDICINE_REQUIRED',
        'FRACTURE', 'SEVERE_FATIGUE', 'OTHER'
    ) NOT NULL,
    reported_severity ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') NOT NULL DEFAULT 'MEDIUM',
    priority_score INT NOT NULL DEFAULT 0,
    priority_level ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') NOT NULL DEFAULT 'LOW',
    priority_reasons TEXT NULL,
    description TEXT NULL,
    medical_attention_required TINYINT(1) DEFAULT 1,
    status ENUM(
        'REPORTED', 'TRIAGE', 'ASSIGNED', 'RESPONDING', 'ARRIVED',
        'TREATMENT', 'REFERRED', 'OBSERVATION', 'RESOLVED', 'CANCELLED', 'CLOSED'
    ) NOT NULL DEFAULT 'REPORTED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    closed_at TIMESTAMP NULL,
    FOREIGN KEY (patient_person_id) REFERENCES person_profiles(id) ON DELETE SET NULL,
    FOREIGN KEY (reported_by_user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_med_case_number (case_number),
    INDEX idx_med_priority (priority_level),
    INDEX idx_med_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 2. MEDICAL_CASE_LOCATIONS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS medical_case_locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    zone VARCHAR(50) NOT NULL, -- Alandi, Pune, Saswad, Jejuri, Lonand, Phaltan, Malshiras, Pandharpur
    route VARCHAR(100) NULL,
    landmark VARCHAR(150) NULL,
    latitude DECIMAL(10, 7) NULL,
    longitude DECIMAL(10, 7) NULL,
    location_description TEXT NULL,
    location_source ENUM('GPS', 'MAP', 'MANUAL', 'VOLUNTEER', 'MEDICAL_CAMP') DEFAULT 'MANUAL',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES medical_cases(id) ON DELETE CASCADE,
    INDEX idx_med_loc_zone (zone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 3. MEDICAL_CASE_SYMPTOMS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS medical_case_symptoms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    symptom VARCHAR(100) NOT NULL,
    severity VARCHAR(20) DEFAULT 'MODERATE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES medical_cases(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 4. MEDICAL_FACILITIES TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS medical_facilities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    facility_code VARCHAR(30) NOT NULL UNIQUE, -- e.g. WS-FAC-001
    name VARCHAR(120) NOT NULL,
    facility_type ENUM('MEDICAL_CAMP', 'FIRST_AID_CENTER', 'HOSPITAL', 'EMERGENCY_CENTER') NOT NULL,
    zone VARCHAR(50) NOT NULL,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    contact_number VARCHAR(15) NOT NULL,
    capacity INT NOT NULL DEFAULT 50,
    current_patients INT NOT NULL DEFAULT 0,
    status ENUM('AVAILABLE', 'BUSY', 'FULL', 'CLOSED', 'EMERGENCY_ONLY') NOT NULL DEFAULT 'AVAILABLE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_fac_zone (zone),
    INDEX idx_fac_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 5. MEDICAL_FACILITY_SERVICES TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS medical_facility_services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    facility_id INT NOT NULL,
    service_name VARCHAR(100) NOT NULL,
    available TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (facility_id) REFERENCES medical_facilities(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 6. MEDICAL_STAFF TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS medical_staff (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    user_id INT NOT NULL,
    staff_code VARCHAR(30) NOT NULL UNIQUE, -- e.g. WS-STF-001
    staff_role ENUM('DOCTOR', 'NURSE', 'PARAMEDIC', 'FIRST_AID_STAFF', 'MEDICAL_COORDINATOR') NOT NULL,
    qualification VARCHAR(100) NULL,
    specialization VARCHAR(100) NULL,
    facility_id INT NULL,
    shift_start VARCHAR(10) DEFAULT '08:00',
    shift_end VARCHAR(10) DEFAULT '20:00',
    status ENUM('ON_DUTY', 'OFF_DUTY', 'ON_CALL') NOT NULL DEFAULT 'ON_DUTY',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (facility_id) REFERENCES medical_facilities(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 7. AMBULANCES TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ambulances (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    ambulance_code VARCHAR(30) NOT NULL UNIQUE, -- e.g. WS-AMB-101
    registration_number VARCHAR(20) NOT NULL UNIQUE,
    ambulance_type ENUM('BASIC_LIFE_SUPPORT', 'ADVANCED_LIFE_SUPPORT', 'PATIENT_TRANSPORT') NOT NULL,
    driver_name VARCHAR(100) NOT NULL,
    driver_contact VARCHAR(15) NOT NULL,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    status ENUM('AVAILABLE', 'ASSIGNED', 'EN_ROUTE', 'AT_SCENE', 'UNAVAILABLE') NOT NULL DEFAULT 'AVAILABLE',
    equipment_description TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 8. AMBULANCE_ASSIGNMENTS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ambulance_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ambulance_id INT NOT NULL,
    case_id INT NOT NULL,
    assigned_by INT NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dispatch_time TIMESTAMP NULL,
    arrival_time TIMESTAMP NULL,
    completion_time TIMESTAMP NULL,
    status ENUM('REQUESTED', 'ASSIGNED', 'DISPATCHED', 'ARRIVED', 'COMPLETED', 'CANCELLED') NOT NULL DEFAULT 'REQUESTED',
    FOREIGN KEY (ambulance_id) REFERENCES ambulances(id) ON DELETE CASCADE,
    FOREIGN KEY (case_id) REFERENCES medical_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 9. MEDICAL_TREATMENTS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS medical_treatments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    medical_staff_id INT NOT NULL,
    facility_id INT NOT NULL,
    assessment TEXT NOT NULL,
    treatment_provided TEXT NOT NULL,
    medication TEXT NULL,
    observation TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES medical_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (medical_staff_id) REFERENCES medical_staff(id) ON DELETE CASCADE,
    FOREIGN KEY (facility_id) REFERENCES medical_facilities(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 10. MEDICAL_REFERRALS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS medical_referrals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    from_facility_id INT NOT NULL,
    to_facility_name VARCHAR(120) NOT NULL,
    reason TEXT NOT NULL,
    ambulance_required TINYINT(1) DEFAULT 1,
    referred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    status ENUM('REFERRED', 'IN_TRANSIT', 'ACCEPTED', 'COMPLETED') DEFAULT 'REFERRED',
    notes TEXT NULL,
    FOREIGN KEY (case_id) REFERENCES medical_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (from_facility_id) REFERENCES medical_facilities(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 11. MEDICAL_CASE_STATUS_HISTORY TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS medical_case_status_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    old_status VARCHAR(30) NULL,
    new_status VARCHAR(30) NOT NULL,
    changed_by INT NOT NULL,
    reason VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES medical_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

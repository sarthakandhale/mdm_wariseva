-- ====================================================================
-- WariSeva Platform - Module 10: Volunteer Management & Task Assignment Schema
-- Case Study: Alandi–Pandharpur Dindi Wari, Maharashtra
-- Database Target: MySQL 8.0+ (integrated with reuniteai DB)
-- ====================================================================

USE reuniteai;

-- --------------------------------------------------------------------
-- 1. VOLUNTEERS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS volunteers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    volunteer_code VARCHAR(30) NOT NULL UNIQUE, -- e.g. WS-VOL-2026-000125
    user_id INT NOT NULL, -- FK to users.id
    person_id INT NULL, -- FK to person_profiles.id
    status ENUM(
        'PENDING_VERIFICATION', 'ACTIVE', 'AVAILABLE', 'BUSY',
        'ON_BREAK', 'OFFLINE', 'SUSPENDED', 'INACTIVE'
    ) NOT NULL DEFAULT 'PENDING_VERIFICATION',
    verification_status ENUM('PENDING', 'VERIFIED', 'REJECTED', 'REQUIRES_UPDATE') NOT NULL DEFAULT 'PENDING',
    experience_years INT DEFAULT 1,
    preferred_zone VARCHAR(50) DEFAULT 'Saswad',
    emergency_contact VARCHAR(30) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES person_profiles(id) ON DELETE SET NULL,
    INDEX idx_vol_code (volunteer_code),
    INDEX idx_vol_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 2. VOLUNTEER_SKILLS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS volunteer_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    volunteer_id INT NOT NULL,
    skill_name VARCHAR(100) NOT NULL,
    skill_level ENUM('BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'CERTIFIED') NOT NULL DEFAULT 'INTERMEDIATE',
    verified TINYINT(1) DEFAULT 0,
    verified_by INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (volunteer_id) REFERENCES volunteers(id) ON DELETE CASCADE,
    FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 3. VOLUNTEER_LANGUAGES TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS volunteer_languages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    volunteer_id INT NOT NULL,
    language VARCHAR(50) NOT NULL,
    proficiency ENUM('BASIC', 'INTERMEDIATE', 'ADVANCED', 'NATIVE') NOT NULL DEFAULT 'ADVANCED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (volunteer_id) REFERENCES volunteers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 4. VOLUNTEER_AVAILABILITY TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS volunteer_availability (
    id INT AUTO_INCREMENT PRIMARY KEY,
    volunteer_id INT NOT NULL,
    availability_date DATE NOT NULL,
    start_time VARCHAR(20) DEFAULT '06:00',
    end_time VARCHAR(20) DEFAULT '14:00',
    zone VARCHAR(50) DEFAULT 'Saswad',
    status ENUM('AVAILABLE', 'BOOKED', 'CANCELLED') NOT NULL DEFAULT 'AVAILABLE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (volunteer_id) REFERENCES volunteers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 5. VOLUNTEER_SHIFTS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS volunteer_shifts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    shift_code VARCHAR(30) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    start_time VARCHAR(20) NOT NULL,
    end_time VARCHAR(20) NOT NULL,
    zone VARCHAR(50) DEFAULT 'Saswad',
    status ENUM('ACTIVE', 'INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 6. VOLUNTEER_ATTENDANCE TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS volunteer_attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    volunteer_id INT NOT NULL,
    shift_id INT NULL,
    check_in TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    check_out TIMESTAMP NULL,
    latitude DECIMAL(10, 7) NULL,
    longitude DECIMAL(10, 7) NULL,
    status ENUM('PRESENT', 'ABSENT', 'ON_DUTY', 'OFF_DUTY') NOT NULL DEFAULT 'ON_DUTY',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (volunteer_id) REFERENCES volunteers(id) ON DELETE CASCADE,
    FOREIGN KEY (shift_id) REFERENCES volunteer_shifts(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 7. VOLUNTEER_TEAMS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS volunteer_teams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    team_code VARCHAR(30) NOT NULL UNIQUE,
    name VARCHAR(120) NOT NULL,
    team_type ENUM(
        'MEDICAL', 'LOST_PERSON', 'HELP_CENTER', 'ROUTE',
        'CROWD_SUPPORT', 'ITEM_RECOVERY', 'DINDI_SUPPORT', 'GENERAL'
    ) NOT NULL DEFAULT 'GENERAL',
    leader_id INT NULL, -- FK to volunteers.id
    zone VARCHAR(50) DEFAULT 'Saswad',
    status ENUM('ACTIVE', 'INACTIVE', 'ON_DUTY', 'OFF_DUTY') NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (leader_id) REFERENCES volunteers(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 8. VOLUNTEER_TEAM_MEMBERS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS volunteer_team_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    team_id INT NOT NULL,
    volunteer_id INT NOT NULL,
    role ENUM('LEADER', 'MEMBER') NOT NULL DEFAULT 'MEMBER',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    left_at TIMESTAMP NULL,
    status ENUM('ACTIVE', 'INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    FOREIGN KEY (team_id) REFERENCES volunteer_teams(id) ON DELETE CASCADE,
    FOREIGN KEY (volunteer_id) REFERENCES volunteers(id) ON DELETE CASCADE,
    UNIQUE KEY uk_team_vol (team_id, volunteer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 9. VOLUNTEER_TASKS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS volunteer_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    task_code VARCHAR(30) NOT NULL UNIQUE, -- e.g. WS-TASK-2026-000456
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    task_type ENUM(
        'MEDICAL_EMERGENCY', 'LOST_PERSON_SEARCH', 'FOUND_PERSON_SUPPORT',
        'LOST_ITEM_SUPPORT', 'ROUTE_ASSISTANCE', 'HELP_CENTER_SUPPORT',
        'CROWD_SUPPORT', 'DINDI_SUPPORT', 'GENERAL_SUPPORT'
    ) NOT NULL DEFAULT 'GENERAL_SUPPORT',
    priority ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') NOT NULL DEFAULT 'MEDIUM',
    source_module VARCHAR(50) DEFAULT 'MANUAL',
    source_case_id VARCHAR(50) NULL,
    zone VARCHAR(50) DEFAULT 'Saswad',
    route_section VARCHAR(100) NULL,
    latitude DECIMAL(10, 7) NULL,
    longitude DECIMAL(10, 7) NULL,
    deadline TIMESTAMP NULL,
    status ENUM(
        'CREATED', 'UNASSIGNED', 'ASSIGNED', 'ACCEPTED', 'IN_PROGRESS',
        'ON_HOLD', 'COMPLETED', 'VERIFIED', 'CANCELLED', 'EXPIRED'
    ) NOT NULL DEFAULT 'UNASSIGNED',
    created_by INT NOT NULL, -- FK to users.id
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_vt_code (task_code),
    INDEX idx_vt_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 10. VOLUNTEER_TASK_REQUIREMENTS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS volunteer_task_requirements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL,
    required_skill VARCHAR(100) NOT NULL,
    minimum_skill_level VARCHAR(50) DEFAULT 'INTERMEDIATE',
    required_language VARCHAR(50) DEFAULT 'Marathi',
    quantity INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES volunteer_tasks(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 11. VOLUNTEER_TASK_ASSIGNMENTS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS volunteer_task_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL,
    volunteer_id INT NOT NULL,
    assigned_by INT NOT NULL, -- FK to users.id
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accepted_at TIMESTAMP NULL,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    declined_at TIMESTAMP NULL,
    decline_reason TEXT NULL,
    status ENUM('ASSIGNED', 'ACCEPTED', 'DECLINED', 'IN_PROGRESS', 'COMPLETED', 'VERIFIED', 'REASSIGNED') NOT NULL DEFAULT 'ASSIGNED',
    FOREIGN KEY (task_id) REFERENCES volunteer_tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (volunteer_id) REFERENCES volunteers(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 12. VOLUNTEER_TASK_HISTORY TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS volunteer_task_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL,
    old_status VARCHAR(50) NULL,
    new_status VARCHAR(50) NOT NULL,
    changed_by INT NOT NULL,
    reason TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES volunteer_tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 13. VOLUNTEER_LOCATION_UPDATES TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS volunteer_location_updates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    volunteer_id INT NOT NULL,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    accuracy REAL DEFAULT 15.0,
    source ENUM('GPS', 'MANUAL') NOT NULL DEFAULT 'GPS',
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (volunteer_id) REFERENCES volunteers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 14. VOLUNTEER_RECOMMENDATIONS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS volunteer_recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL,
    volunteer_id INT NOT NULL,
    skill_score INT DEFAULT 0,
    location_score INT DEFAULT 0,
    availability_score INT DEFAULT 0,
    language_score INT DEFAULT 0,
    workload_score INT DEFAULT 0,
    experience_score INT DEFAULT 0,
    total_score INT DEFAULT 0,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('RECOMMENDED', 'ACCEPTED', 'REJECTED') NOT NULL DEFAULT 'RECOMMENDED',
    FOREIGN KEY (task_id) REFERENCES volunteer_tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (volunteer_id) REFERENCES volunteers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

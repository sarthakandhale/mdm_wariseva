-- ====================================================================
-- WariSeva Platform - Module 7: AI-Assisted Matching & Recommendation Schema
-- Case Study: Alandi–Pandharpur Dindi Wari, Maharashtra
-- Database Target: MySQL 8.0+ (integrated with reuniteai DB)
-- ====================================================================

USE reuniteai;

-- --------------------------------------------------------------------
-- 1. AI_MATCH_RESULTS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ai_match_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    match_type ENUM('PERSON', 'ITEM') NOT NULL DEFAULT 'PERSON',
    source_case_id INT NOT NULL, -- Lost Person Case ID or Lost Item Case ID
    candidate_case_id INT NOT NULL, -- Found Person Case ID or Found Item Case ID
    match_score INT NOT NULL, -- 0 to 100 percentage
    confidence_score INT NOT NULL, -- 0 to 100 percentage based on data quality
    data_quality_score INT NOT NULL, -- 0 to 100 percentage based on field completeness
    explanation TEXT NULL, -- JSON string of contributing factors and bullet points
    model_version VARCHAR(50) DEFAULT 'v1.0-Hybrid',
    status ENUM(
        'GENERATED', 'UNDER_REVIEW', 'ACCEPTED_FOR_VERIFICATION',
        'REJECTED', 'VERIFIED', 'FALSE_MATCH', 'EXPIRED'
    ) NOT NULL DEFAULT 'GENERATED',
    reviewed_by INT NULL, -- FK to users.id
    reviewed_at TIMESTAMP NULL,
    review_notes TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_aim_type (match_type),
    INDEX idx_aim_source (source_case_id),
    INDEX idx_aim_candidate (candidate_case_id),
    INDEX idx_aim_score (match_score),
    INDEX idx_aim_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

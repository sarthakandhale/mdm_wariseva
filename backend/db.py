import os
import sqlite3
from werkzeug.security import generate_password_hash
from config import Config

try:
    import pymysql
    import pymysql.cursors
    HAS_PYMYSQL = True
except ImportError:
    HAS_PYMYSQL = False

def get_db_connection():
    """
    Attempts to connect to MySQL database first (if pymysql installed).
    If MySQL server is not running locally or pymysql is missing, 
    seamlessly falls back to SQLite to guarantee out-of-the-box local execution.
    """
    if HAS_PYMYSQL:
        try:
            conn = pymysql.connect(
                host=Config.MYSQL_HOST,
                port=Config.MYSQL_PORT,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DB,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=3
            )
            return conn, 'mysql'
        except Exception:
            pass

    # Fallback to SQLite database file
    db_path = Config.SQLITE_PATH
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    init_sqlite_if_needed(conn)
    return conn, 'sqlite'


def init_sqlite_if_needed(conn):
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS permissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS role_permissions (
        role_id INTEGER NOT NULL,
        permission_id INTEGER NOT NULL,
        PRIMARY KEY (role_id, permission_id)
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        mobile TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE,
        password_hash TEXT NOT NULL,
        role_id INTEGER NOT NULL,
        profile_photo TEXT,
        preferred_language TEXT DEFAULT 'en',
        status TEXT NOT NULL DEFAULT 'PENDING',
        is_verified INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_login_at DATETIME
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        session_token TEXT UNIQUE NOT NULL,
        ip_address TEXT,
        user_agent TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        expires_at DATETIME NOT NULL,
        revoked_at DATETIME
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS password_reset_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token TEXT UNIQUE NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        expires_at DATETIME NOT NULL,
        used_at DATETIME
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT NOT NULL,
        details TEXT,
        ip_address TEXT,
        user_agent TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # ------------------ Module 2 Tables ------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS families (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE NOT NULL,
        family_code TEXT UNIQUE NOT NULL,
        family_name TEXT NOT NULL,
        owner_user_id INTEGER NOT NULL,
        primary_contact_name TEXT NOT NULL,
        primary_contact_mobile TEXT NOT NULL,
        emergency_contact_name TEXT NOT NULL,
        emergency_contact_mobile TEXT NOT NULL,
        preferred_language TEXT DEFAULT 'en',
        notes TEXT,
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS person_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE NOT NULL,
        person_code TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        date_of_birth DATE NOT NULL,
        gender TEXT NOT NULL,
        age_category TEXT NOT NULL,
        height TEXT,
        approx_weight TEXT,
        hair_color TEXT,
        eye_color TEXT,
        skin_tone TEXT,
        identification_mark TEXT,
        glasses INTEGER DEFAULT 0,
        hearing_aid INTEGER DEFAULT 0,
        walking_assistance INTEGER DEFAULT 0,
        preferred_language TEXT DEFAULT 'en',
        profile_visibility TEXT DEFAULT 'PRIVATE',
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS family_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE NOT NULL,
        family_id INTEGER NOT NULL,
        person_id INTEGER NOT NULL,
        relationship_type TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (family_id, person_id)
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS person_photos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE NOT NULL,
        person_id INTEGER NOT NULL,
        file_path TEXT NOT NULL,
        file_type TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        is_primary INTEGER DEFAULT 1,
        uploaded_by INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clothing_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_id INTEGER UNIQUE NOT NULL,
        top_type TEXT,
        top_color TEXT,
        bottom_type TEXT,
        bottom_color TEXT,
        footwear TEXT,
        footwear_color TEXT,
        headwear TEXT,
        accessories TEXT,
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS person_safety_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_id INTEGER UNIQUE NOT NULL,
        medical_condition TEXT,
        medication_requirement TEXT,
        allergy_information TEXT,
        blood_group TEXT,
        mobility_assistance TEXT,
        communication_difficulty TEXT,
        cognitive_assistance_required INTEGER DEFAULT 0,
        consent_status INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS emergency_contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_id INTEGER NOT NULL,
        contact_name TEXT NOT NULL,
        relationship TEXT NOT NULL,
        mobile TEXT NOT NULL,
        alternate_mobile TEXT,
        is_primary INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS family_access (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        family_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        access_level TEXT NOT NULL DEFAULT 'VIEWER',
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (family_id, user_id)
    );
    """)
    
    # ------------------ Module 3 Tables ------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medical_cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE NOT NULL,
        case_number TEXT UNIQUE NOT NULL,
        patient_person_id INTEGER,
        temp_patient_code TEXT,
        temp_patient_name TEXT,
        temp_patient_age INTEGER,
        temp_patient_gender TEXT,
        temp_patient_description TEXT,
        reported_by_user_id INTEGER NOT NULL,
        emergency_type TEXT NOT NULL,
        reported_severity TEXT DEFAULT 'MEDIUM',
        priority_score INTEGER DEFAULT 0,
        priority_level TEXT DEFAULT 'LOW',
        priority_reasons TEXT,
        description TEXT,
        medical_attention_required INTEGER DEFAULT 1,
        status TEXT NOT NULL DEFAULT 'REPORTED',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        closed_at DATETIME
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medical_case_locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL,
        zone TEXT NOT NULL,
        route TEXT,
        landmark TEXT,
        latitude REAL,
        longitude REAL,
        location_description TEXT,
        location_source TEXT DEFAULT 'MANUAL',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medical_case_symptoms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL,
        symptom TEXT NOT NULL,
        severity TEXT DEFAULT 'MODERATE',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medical_facilities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE NOT NULL,
        facility_code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        facility_type TEXT NOT NULL,
        zone TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        contact_number TEXT NOT NULL,
        capacity INTEGER DEFAULT 50,
        current_patients INTEGER DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'AVAILABLE',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medical_facility_services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        facility_id INTEGER NOT NULL,
        service_name TEXT NOT NULL,
        available INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medical_staff (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        staff_code TEXT UNIQUE NOT NULL,
        staff_role TEXT NOT NULL,
        qualification TEXT,
        specialization TEXT,
        facility_id INTEGER,
        shift_start TEXT DEFAULT '08:00',
        shift_end TEXT DEFAULT '20:00',
        status TEXT DEFAULT 'ON_DUTY',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ambulances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE NOT NULL,
        ambulance_code TEXT UNIQUE NOT NULL,
        registration_number TEXT UNIQUE NOT NULL,
        ambulance_type TEXT NOT NULL,
        driver_name TEXT NOT NULL,
        driver_contact TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        status TEXT DEFAULT 'AVAILABLE',
        equipment_description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ambulance_assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ambulance_id INTEGER NOT NULL,
        case_id INTEGER NOT NULL,
        assigned_by INTEGER NOT NULL,
        assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        dispatch_time DATETIME,
        arrival_time DATETIME,
        completion_time DATETIME,
        status TEXT DEFAULT 'REQUESTED'
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medical_treatments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL,
        medical_staff_id INTEGER NOT NULL,
        facility_id INTEGER NOT NULL,
        assessment TEXT NOT NULL,
        treatment_provided TEXT NOT NULL,
        medication TEXT,
        observation TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medical_referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL,
        from_facility_id INTEGER NOT NULL,
        to_facility_name TEXT NOT NULL,
        reason TEXT NOT NULL,
        ambulance_required INTEGER DEFAULT 1,
        referred_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        completed_at DATETIME,
        status TEXT DEFAULT 'REFERRED',
        notes TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medical_case_status_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL,
        old_status TEXT,
        new_status TEXT NOT NULL,
        changed_by INTEGER NOT NULL,
        reason TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # ------------------ Module 4 Tables ------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lost_person_cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE NOT NULL,
        case_number TEXT UNIQUE NOT NULL,
        person_id INTEGER,
        temp_person_code TEXT,
        temp_person_name TEXT,
        temp_person_age INTEGER,
        temp_person_gender TEXT,
        temp_person_description TEXT,
        family_id INTEGER,
        dindi_id INTEGER,
        reported_by_user_id INTEGER NOT NULL,
        reporter_relationship TEXT NOT NULL,
        reported_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_seen_at DATETIME NOT NULL,
        priority_score INTEGER DEFAULT 0,
        priority_level TEXT DEFAULT 'LOW',
        priority_reasons TEXT,
        is_priority_overridden INTEGER DEFAULT 0,
        override_reason TEXT,
        overridden_by INTEGER,
        overridden_at DATETIME,
        status TEXT NOT NULL DEFAULT 'REPORTED',
        additional_information TEXT,
        medical_attention_required INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        closed_at DATETIME
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lost_person_locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL,
        zone TEXT NOT NULL,
        route_section TEXT,
        landmark TEXT,
        dindi_id INTEGER,
        latitude REAL,
        longitude REAL,
        location_description TEXT,
        location_source TEXT DEFAULT 'MANUAL',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lost_person_clothing (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL,
        top_type TEXT,
        top_color TEXT,
        bottom_type TEXT,
        bottom_color TEXT,
        footwear TEXT,
        footwear_color TEXT,
        headwear TEXT,
        accessories TEXT,
        description TEXT,
        confirmed_from_profile INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lost_person_status_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL,
        old_status TEXT,
        new_status TEXT NOT NULL,
        changed_by INTEGER NOT NULL,
        reason TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lost_person_attachments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL,
        uploaded_by INTEGER NOT NULL,
        file_path TEXT NOT NULL,
        file_name TEXT NOT NULL,
        file_type TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lost_person_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL,
        created_by INTEGER NOT NULL,
        note TEXT NOT NULL,
        visibility TEXT DEFAULT 'FAMILY_VISIBLE',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lost_person_search_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL,
        requested_by INTEGER NOT NULL,
        zone TEXT NOT NULL,
        priority TEXT DEFAULT 'HIGH',
        description TEXT,
        status TEXT DEFAULT 'REQUESTED',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lost_person_sightings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL,
        reported_by INTEGER NOT NULL,
        location_description TEXT NOT NULL,
        zone TEXT NOT NULL,
        latitude REAL,
        longitude REAL,
        sighting_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        description TEXT,
        photo_path TEXT,
        confidence_rating TEXT DEFAULT 'MEDIUM',
        status TEXT DEFAULT 'REPORTED',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # ------------------ Module 5 Tables ------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS found_person_cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE NOT NULL,
        case_number TEXT UNIQUE NOT NULL,
        temporary_person_id TEXT UNIQUE NOT NULL,
        linked_person_id INTEGER,
        reported_by_user_id INTEGER NOT NULL,
        identification_status TEXT NOT NULL DEFAULT 'UNIDENTIFIED_PERSON',
        approximate_name TEXT,
        approximate_age INTEGER,
        gender TEXT,
        language TEXT DEFAULT 'Marathi',
        communication_status TEXT DEFAULT 'CAN_COMMUNICATE',
        medical_attention_required INTEGER DEFAULT 0,
        medical_case_id INTEGER,
        special_assistance_required TEXT,
        dindi_id INTEGER,
        status TEXT NOT NULL DEFAULT 'REPORTED',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        closed_at DATETIME
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS found_person_locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL,
        zone TEXT NOT NULL,
        route_section TEXT,
        landmark TEXT,
        dindi_id INTEGER,
        latitude REAL,
        longitude REAL,
        location_description TEXT,
        location_source TEXT DEFAULT 'VOLUNTEER',
        found_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS found_person_clothing (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL,
        top_type TEXT,
        top_color TEXT,
        bottom_type TEXT,
        bottom_color TEXT,
        footwear TEXT,
        footwear_color TEXT,
        headwear TEXT,
        accessories TEXT,
        description TEXT,
        confidence_level TEXT DEFAULT 'HIGH',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS found_person_photos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL,
        uploaded_by INTEGER NOT NULL,
        file_path TEXT NOT NULL,
        file_type TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        is_primary INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS found_person_identification_clues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL,
        clue_type TEXT NOT NULL,
        clue_value TEXT NOT NULL,
        source TEXT DEFAULT 'Person verbal statement',
        confidence TEXT DEFAULT 'MEDIUM',
        verified INTEGER DEFAULT 0,
        verified_by INTEGER,
        verified_at DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS found_person_safe_locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL,
        facility_type TEXT NOT NULL DEFAULT 'HELP_CENTER',
        facility_id INTEGER,
        location_name TEXT NOT NULL,
        arrival_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        departure_time DATETIME,
        status TEXT NOT NULL DEFAULT 'AT_HELP_CENTER',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS found_person_family_contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL,
        contact_name TEXT NOT NULL,
        contact_number TEXT NOT NULL,
        relationship TEXT,
        contact_method TEXT DEFAULT 'Phone Call',
        contacted_by INTEGER NOT NULL,
        contacted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        result TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS found_person_verifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL,
        verification_status TEXT NOT NULL DEFAULT 'NOT_STARTED',
        verification_method TEXT NOT NULL DEFAULT 'PERSONAL_INFORMATION',
        verified_by INTEGER NOT NULL,
        verification_notes TEXT,
        verified_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS found_person_reunifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL,
        reunited_with TEXT NOT NULL,
        verified_by INTEGER NOT NULL,
        reunification_location TEXT NOT NULL,
        reunification_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        verification_method TEXT DEFAULT 'FAMILY_CONFIRMATION',
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS found_person_status_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL,
        old_status TEXT,
        new_status TEXT NOT NULL,
        changed_by INTEGER NOT NULL,
        reason TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS found_person_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL,
        created_by INTEGER NOT NULL,
        note TEXT NOT NULL,
        visibility TEXT DEFAULT 'FAMILY_VISIBLE',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # ------------------ Module 6 Tables ------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lost_item_cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE NOT NULL,
        case_number TEXT UNIQUE NOT NULL,
        reported_by_user_id INTEGER NOT NULL,
        item_category TEXT NOT NULL DEFAULT 'OTHER',
        item_name TEXT NOT NULL,
        brand TEXT,
        model TEXT,
        color TEXT,
        description TEXT,
        approximate_value REAL DEFAULT 0.0,
        serial_number TEXT,
        imei TEXT,
        status TEXT NOT NULL DEFAULT 'REPORTED',
        dindi_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        closed_at DATETIME
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS found_item_cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE NOT NULL,
        case_number TEXT UNIQUE NOT NULL,
        reported_by_user_id INTEGER NOT NULL,
        item_category TEXT NOT NULL DEFAULT 'OTHER',
        item_name TEXT NOT NULL,
        brand TEXT,
        model TEXT,
        color TEXT,
        description TEXT,
        condition TEXT NOT NULL DEFAULT 'GOOD',
        dindi_id INTEGER,
        found_by_user_id INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'REPORTED',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        closed_at DATETIME
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS item_photos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lost_item_case_id INTEGER,
        found_item_case_id INTEGER,
        uploaded_by INTEGER NOT NULL,
        file_path TEXT NOT NULL,
        file_type TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        is_primary INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS item_locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lost_item_case_id INTEGER,
        found_item_case_id INTEGER,
        zone TEXT NOT NULL,
        route_section TEXT,
        landmark TEXT,
        latitude REAL,
        longitude REAL,
        location_type TEXT NOT NULL DEFAULT 'LOST',
        location_description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS item_identifiers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lost_item_case_id INTEGER,
        found_item_case_id INTEGER,
        identifier_type TEXT NOT NULL,
        identifier_value TEXT NOT NULL,
        visibility TEXT NOT NULL DEFAULT 'AUTHORIZED_ONLY',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS item_claims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        claim_number TEXT UNIQUE NOT NULL,
        found_item_case_id INTEGER NOT NULL,
        claimed_by_user_id INTEGER NOT NULL,
        claim_description TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'SUBMITTED',
        submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        reviewed_by INTEGER,
        reviewed_at DATETIME
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS item_claim_verifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        claim_id INTEGER NOT NULL,
        verification_type TEXT NOT NULL,
        verification_result TEXT NOT NULL DEFAULT 'MATCH',
        verification_notes TEXT,
        verified_by INTEGER NOT NULL,
        verified_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS item_storage_locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        facility_name TEXT NOT NULL,
        facility_code TEXT UNIQUE NOT NULL,
        locker TEXT NOT NULL,
        shelf TEXT,
        capacity INTEGER DEFAULT 50,
        current_count INTEGER DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'AVAILABLE',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS item_custody_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        found_item_case_id INTEGER NOT NULL,
        from_user_id INTEGER,
        to_user_id INTEGER NOT NULL,
        from_location TEXT,
        to_location TEXT NOT NULL,
        action TEXT NOT NULL DEFAULT 'RECEIVED',
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS item_status_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lost_item_case_id INTEGER,
        found_item_case_id INTEGER,
        old_status TEXT,
        new_status TEXT NOT NULL,
        changed_by INTEGER NOT NULL,
        reason TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS item_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lost_item_case_id INTEGER,
        found_item_case_id INTEGER,
        created_by INTEGER NOT NULL,
        note TEXT NOT NULL,
        visibility TEXT DEFAULT 'USER_VISIBLE',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS item_matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lost_item_case_id INTEGER NOT NULL,
        found_item_case_id INTEGER NOT NULL,
        match_type TEXT NOT NULL DEFAULT 'MANUAL',
        match_score INTEGER DEFAULT 100,
        match_reason TEXT,
        created_by INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'MANUAL_POTENTIAL_MATCH',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # ------------------ Module 7 Tables ------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_match_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE NOT NULL,
        match_type TEXT NOT NULL DEFAULT 'PERSON',
        source_case_id INTEGER NOT NULL,
        candidate_case_id INTEGER NOT NULL,
        match_score INTEGER NOT NULL,
        confidence_score INTEGER NOT NULL,
        data_quality_score INTEGER NOT NULL,
        explanation TEXT,
        model_version TEXT DEFAULT 'v1.0-Hybrid',
        status TEXT NOT NULL DEFAULT 'GENERATED',
        reviewed_by INTEGER,
        reviewed_at DATETIME,
        review_notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # ------------------ Module 8 Tables ------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dindis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE NOT NULL,
        dindi_code TEXT UNIQUE NOT NULL,
        dindi_number INTEGER UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        registration_year INTEGER DEFAULT 2026,
        start_location TEXT DEFAULT 'Alandi',
        destination TEXT DEFAULT 'Pandharpur',
        expected_member_count INTEGER DEFAULT 100,
        status TEXT NOT NULL DEFAULT 'PENDING',
        created_by INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dindi_leaders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dindi_id INTEGER NOT NULL,
        person_id INTEGER,
        user_id INTEGER NOT NULL,
        role TEXT NOT NULL DEFAULT 'PRIMARY_LEADER',
        start_date TEXT,
        end_date TEXT,
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dindi_memberships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dindi_id INTEGER NOT NULL,
        person_id INTEGER NOT NULL,
        membership_number TEXT,
        role TEXT NOT NULL DEFAULT 'MEMBER',
        joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        left_at DATETIME,
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(dindi_id, person_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dindi_schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dindi_id INTEGER NOT NULL,
        schedule_date TEXT NOT NULL,
        start_location TEXT NOT NULL,
        end_location TEXT NOT NULL,
        expected_start_time TEXT DEFAULT '05:30 AM',
        expected_arrival_time TEXT DEFAULT '06:00 PM',
        rest_point TEXT,
        notes TEXT,
        status TEXT NOT NULL DEFAULT 'SCHEDULED',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dindi_announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dindi_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        priority TEXT NOT NULL DEFAULT 'NORMAL',
        created_by INTEGER NOT NULL,
        published_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        expiry_at DATETIME,
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dindi_contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dindi_id INTEGER NOT NULL,
        contact_type TEXT NOT NULL DEFAULT 'PRIMARY',
        contact_name TEXT NOT NULL,
        contact_number TEXT NOT NULL,
        visibility TEXT NOT NULL DEFAULT 'PUBLIC',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dindi_verifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dindi_id INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'VERIFIED',
        verified_by INTEGER NOT NULL,
        verification_notes TEXT,
        verified_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dindi_documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dindi_id INTEGER NOT NULL,
        uploaded_by INTEGER NOT NULL,
        file_path TEXT NOT NULL,
        file_name TEXT NOT NULL,
        file_type TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dindi_route_associations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dindi_id INTEGER NOT NULL,
        route_id INTEGER DEFAULT 101,
        sequence_number INTEGER DEFAULT 1,
        start_date TEXT,
        end_date TEXT,
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # ------------------ Module 9 Tables ------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wari_routes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE NOT NULL,
        route_code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        start_location TEXT NOT NULL DEFAULT 'Alandi',
        destination TEXT NOT NULL DEFAULT 'Pandharpur',
        total_distance REAL DEFAULT 242.50,
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS route_sections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        route_id INTEGER NOT NULL,
        section_code TEXT UNIQUE NOT NULL,
        sequence_number INTEGER NOT NULL,
        start_location TEXT NOT NULL,
        end_location TEXT NOT NULL,
        distance_km REAL NOT NULL,
        estimated_duration TEXT DEFAULT '1 Day',
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS route_points (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        route_section_id INTEGER NOT NULL,
        sequence_number INTEGER NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        point_name TEXT,
        point_type TEXT NOT NULL DEFAULT 'WAYPOINT',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wari_locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        location_type TEXT NOT NULL DEFAULT 'OTHER',
        route_section_id INTEGER,
        zone TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        description TEXT,
        contact_number TEXT,
        status TEXT NOT NULL DEFAULT 'OPEN',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dindi_location_updates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dindi_id INTEGER NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        accuracy REAL DEFAULT 15.0,
        location_source TEXT NOT NULL DEFAULT 'MANUAL',
        status TEXT NOT NULL DEFAULT 'MOVING',
        recorded_by INTEGER NOT NULL,
        recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dindi_checkins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dindi_id INTEGER NOT NULL,
        checkpoint_id INTEGER NOT NULL,
        checked_in_by INTEGER NOT NULL,
        latitude REAL,
        longitude REAL,
        checked_in_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        status TEXT NOT NULL DEFAULT 'PASSED'
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS route_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        route_section_id INTEGER,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        priority TEXT NOT NULL DEFAULT 'NORMAL',
        created_by INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        expiry_at DATETIME,
        status TEXT NOT NULL DEFAULT 'ACTIVE'
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS crowd_zones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        zone_code TEXT UNIQUE NOT NULL,
        zone_name TEXT NOT NULL,
        route_section_id INTEGER,
        crowd_level TEXT NOT NULL DEFAULT 'LOW',
        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_by INTEGER NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS emergency_zones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        zone_code TEXT UNIQUE NOT NULL,
        route_section_id INTEGER,
        reason TEXT NOT NULL,
        priority TEXT NOT NULL DEFAULT 'HIGH',
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        active_from DATETIME DEFAULT CURRENT_TIMESTAMP,
        active_until DATETIME,
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        created_by INTEGER NOT NULL
    );
    """)

    # ------------------ Module 10 Tables ------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS volunteers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE NOT NULL,
        volunteer_code TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        person_id INTEGER,
        status TEXT NOT NULL DEFAULT 'PENDING_VERIFICATION',
        verification_status TEXT NOT NULL DEFAULT 'PENDING',
        experience_years INTEGER DEFAULT 1,
        preferred_zone TEXT DEFAULT 'Saswad',
        emergency_contact TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS volunteer_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        volunteer_id INTEGER NOT NULL,
        skill_name TEXT NOT NULL,
        skill_level TEXT NOT NULL DEFAULT 'INTERMEDIATE',
        verified INTEGER DEFAULT 0,
        verified_by INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS volunteer_languages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        volunteer_id INTEGER NOT NULL,
        language TEXT NOT NULL,
        proficiency TEXT NOT NULL DEFAULT 'ADVANCED',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS volunteer_availability (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        volunteer_id INTEGER NOT NULL,
        availability_date TEXT NOT NULL,
        start_time TEXT DEFAULT '06:00',
        end_time TEXT DEFAULT '14:00',
        zone TEXT DEFAULT 'Saswad',
        status TEXT NOT NULL DEFAULT 'AVAILABLE',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS volunteer_shifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        shift_code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        zone TEXT DEFAULT 'Saswad',
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS volunteer_attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        volunteer_id INTEGER NOT NULL,
        shift_id INTEGER,
        check_in DATETIME DEFAULT CURRENT_TIMESTAMP,
        check_out DATETIME,
        latitude REAL,
        longitude REAL,
        status TEXT NOT NULL DEFAULT 'ON_DUTY',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS volunteer_teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        team_type TEXT NOT NULL DEFAULT 'GENERAL',
        leader_id INTEGER,
        zone TEXT DEFAULT 'Saswad',
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS volunteer_team_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_id INTEGER NOT NULL,
        volunteer_id INTEGER NOT NULL,
        role TEXT NOT NULL DEFAULT 'MEMBER',
        joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        left_at DATETIME,
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        UNIQUE(team_id, volunteer_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS volunteer_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE NOT NULL,
        task_code TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        task_type TEXT NOT NULL DEFAULT 'GENERAL_SUPPORT',
        priority TEXT NOT NULL DEFAULT 'MEDIUM',
        source_module TEXT DEFAULT 'MANUAL',
        source_case_id TEXT,
        zone TEXT DEFAULT 'Saswad',
        route_section TEXT,
        latitude REAL,
        longitude REAL,
        deadline DATETIME,
        status TEXT NOT NULL DEFAULT 'UNASSIGNED',
        created_by INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        completed_at DATETIME
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS volunteer_task_requirements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        required_skill TEXT NOT NULL,
        minimum_skill_level TEXT DEFAULT 'INTERMEDIATE',
        required_language TEXT DEFAULT 'Marathi',
        quantity INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS volunteer_task_assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        volunteer_id INTEGER NOT NULL,
        assigned_by INTEGER NOT NULL,
        assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        accepted_at DATETIME,
        started_at DATETIME,
        completed_at DATETIME,
        declined_at DATETIME,
        decline_reason TEXT,
        status TEXT NOT NULL DEFAULT 'ASSIGNED'
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS volunteer_task_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        old_status TEXT,
        new_status TEXT NOT NULL,
        changed_by INTEGER NOT NULL,
        reason TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS volunteer_location_updates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        volunteer_id INTEGER NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        accuracy REAL DEFAULT 15.0,
        source TEXT NOT NULL DEFAULT 'GPS',
        recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS volunteer_recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        volunteer_id INTEGER NOT NULL,
        skill_score INTEGER DEFAULT 0,
        location_score INTEGER DEFAULT 0,
        availability_score INTEGER DEFAULT 0,
        language_score INTEGER DEFAULT 0,
        workload_score INTEGER DEFAULT 0,
        experience_score INTEGER DEFAULT 0,
        total_score INTEGER DEFAULT 0,
        generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        status TEXT NOT NULL DEFAULT 'RECOMMENDED'
    );
    """)







    
    # Check if roles are seeded
    cursor.execute("SELECT COUNT(*) as count FROM roles;")
    row = cursor.fetchone()
    if row['count'] == 0:
        seed_sqlite_data(cursor)
        conn.commit()
    else:
        # Check if Module 2 family seed is present
        cursor.execute("SELECT COUNT(*) as count FROM families;")
        fam_row = cursor.fetchone()
        if fam_row['count'] == 0:
            seed_module2_sqlite(cursor)
            conn.commit()

        # Check if Module 3 seed is present
        cursor.execute("SELECT COUNT(*) as count FROM medical_facilities;")
        med_row = cursor.fetchone()
        if med_row['count'] == 0:
            seed_module3_sqlite(cursor)
            conn.commit()

        # Check if Module 4 seed is present
        cursor.execute("SELECT COUNT(*) as count FROM lost_person_cases;")
        lost_row = cursor.fetchone()
        if lost_row['count'] == 0:
            seed_module4_sqlite(cursor)
            conn.commit()

        # Check if Module 5 seed is present
        cursor.execute("SELECT COUNT(*) as count FROM found_person_cases;")
        found_row = cursor.fetchone()
        if found_row['count'] == 0:
            seed_module5_sqlite(cursor)
            conn.commit()

        # Check if Module 6 seed is present
        cursor.execute("SELECT COUNT(*) as count FROM lost_item_cases;")
        item_row = cursor.fetchone()
        if item_row['count'] == 0:
            seed_module6_sqlite(cursor)
            conn.commit()

        # Check if Module 7 seed is present
        cursor.execute("SELECT COUNT(*) as count FROM ai_match_results;")
        ai_row = cursor.fetchone()
        if ai_row['count'] == 0:
            seed_module7_sqlite(cursor)
            conn.commit()

        # Check if Module 8 seed is present
        cursor.execute("SELECT COUNT(*) as count FROM dindis;")
        din_row = cursor.fetchone()
        if din_row['count'] == 0:
            seed_module8_sqlite(cursor)
            conn.commit()

        # Check if Module 9 seed is present
        cursor.execute("SELECT COUNT(*) as count FROM wari_routes;")
        rt_row = cursor.fetchone()
        if rt_row['count'] == 0:
            seed_module9_sqlite(cursor)
            conn.commit()

        # Check if Module 10 seed is present
        cursor.execute("SELECT COUNT(*) as count FROM volunteers;")
        vol_row = cursor.fetchone()
        if vol_row['count'] == 0:
            seed_module10_sqlite(cursor)
            conn.commit()










def seed_sqlite_data(cursor):
    roles = [
        (1, 'PARENT_GUARDIAN', 'Parent or guardian registering family members and reporting missing persons'),
        (2, 'VOLUNTEER', 'Ground volunteer assisting in search, reporting found individuals'),
        (3, 'POLICE_OFFICER', 'Law enforcement official managing cases and verification'),
        (4, 'MEDICAL_STAFF', 'Medical center staff logging unclaimed individuals'),
        (5, 'HELP_CENTER_OPERATOR', 'Kiosk/Help desk staff managing lost & found inquiries'),
        (6, 'EVENT_ADMIN', 'Event manager overseeing logistics and staff approvals'),
        (7, 'SUPER_ADMIN', 'System administrator with full permissions')
    ]
    cursor.executemany("INSERT INTO roles (id, name, description) VALUES (?, ?, ?);", roles)
    
    permissions = [
        (1, 'USER_VIEW', 'View user profiles and list users'),
        (2, 'USER_CREATE', 'Register or create new system users'),
        (3, 'USER_UPDATE', 'Update user profiles and details'),
        (4, 'USER_DELETE', 'Delete or remove users'),
        (5, 'PROFILE_VIEW', 'View own profile information'),
        (6, 'PROFILE_UPDATE', 'Update own profile information'),
        (7, 'CASE_VIEW', 'View missing/found person cases'),
        (8, 'CASE_CREATE', 'Report missing person case'),
        (9, 'CASE_UPDATE', 'Update missing person case status'),
        (10, 'FOUND_PERSON_CREATE', 'Report found person or item'),
        (11, 'MATCH_VIEW', 'View AI face and profile match results'),
        (12, 'MATCH_VERIFY', 'Confirm or reject person reunification match'),
        (13, 'VOLUNTEER_ASSIGN', 'Assign volunteers to active search sectors'),
        (14, 'REPORT_VIEW', 'View overall platform reports and analytics'),
        (15, 'ADMIN_APPROVE_USER', 'Approve, suspend, block, or reject user registrations'),
        (16, 'AUDIT_VIEW', 'View security audit logs and system events')
    ]
    cursor.executemany("INSERT INTO permissions (id, name, description) VALUES (?, ?, ?);", permissions)
    
    # Role permissions
    rp = [
        # PARENT
        (1,5), (1,6), (1,7), (1,8), (1,9),
        # VOLUNTEER
        (2,5), (2,6), (2,7), (2,10), (2,11),
        # POLICE
        (3,5), (3,6), (3,7), (3,8), (3,9), (3,10), (3,11), (3,12), (3,13), (3,14),
        # MEDICAL
        (4,5), (4,6), (4,7), (4,10), (4,11),
        # HELP CENTER
        (5,5), (5,6), (5,7), (5,8), (5,9), (5,10), (5,11), (5,12),
        # EVENT ADMIN
        (6,1), (6,2), (6,3), (6,5), (6,6), (6,7), (6,8), (6,9), (6,10), (6,11), (6,12), (6,13), (6,14), (6,15),
        # SUPER ADMIN
        (7,1), (7,2), (7,3), (7,4), (7,5), (7,6), (7,7), (7,8), (7,9), (7,10), (7,11), (7,12), (7,13), (7,14), (7,15), (7,16)
    ]
    cursor.executemany("INSERT INTO role_permissions (role_id, permission_id) VALUES (?, ?);", rp)
    
    # Standard password hash for 'Demo1234!'
    pwd_hash = generate_password_hash('Demo1234!')
    
    users = [
        (1, 'usr-super-admin-001', 'System Administrator', '9876543210', 'admin@demo.com', pwd_hash, 7, None, 'en', 'ACTIVE', 1),
        (2, 'usr-event-admin-002', 'Event Administrator', '9876543211', 'eventadmin@demo.com', pwd_hash, 6, None, 'en', 'ACTIVE', 1),
        (3, 'usr-police-003', 'Inspector Rajesh Kumar', '9876543212', 'police@demo.com', pwd_hash, 3, None, 'or', 'ACTIVE', 1),
        (4, 'usr-helpdesk-004', 'Sita Sharma (Help Desk)', '9876543213', 'helpcenter@demo.com', pwd_hash, 5, None, 'or', 'ACTIVE', 1),
        (5, 'usr-medical-005', 'Dr. Ananya Dash', '9876543214', 'medical@demo.com', pwd_hash, 4, None, 'en', 'ACTIVE', 1),
        (6, 'usr-volunteer-006', 'Amitabh Mohanty', '9876543215', 'volunteer@demo.com', pwd_hash, 2, None, 'hi', 'ACTIVE', 1),
        (7, 'usr-parent-007', 'Ramesh Chandra Swain', '9876543216', 'parent@demo.com', pwd_hash, 1, None, 'or', 'ACTIVE', 1),
        (8, 'usr-volunteer-008', 'Priya Sahoo (Pending)', '9876543217', 'priya.v@demo.com', pwd_hash, 2, None, 'or', 'PENDING', 0),
        (9, 'usr-police-009', 'Sub-Inspector Manoj Jena', '9876543218', 'manoj.police@demo.com', pwd_hash, 3, None, 'or', 'PENDING', 0)
    ]
    cursor.executemany("""
    INSERT INTO users (id, uuid, full_name, mobile, email, password_hash, role_id, profile_photo, preferred_language, status, is_verified)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, users)
    
    cursor.execute("""
    INSERT INTO audit_logs (user_id, action, details, ip_address, user_agent)
    VALUES (1, 'SYSTEM_INIT', 'ReuniteAI initialized with seed roles and demo accounts', '127.0.0.1', 'System/Initializer');
    """)
    seed_module2_sqlite(cursor)

def seed_module2_sqlite(cursor):
    cursor.execute("""
    INSERT INTO families (id, uuid, family_code, family_name, owner_user_id, primary_contact_name, primary_contact_mobile, emergency_contact_name, emergency_contact_mobile, preferred_language, status)
    VALUES (1, 'fam-patil-001', 'RY-FAM-2026-000001', 'Patil Family', 7, 'Ramesh Chandra Swain', '9876543216', 'Amit Patil', '9988776655', 'or', 'ACTIVE');
    """)

    cursor.execute("""
    INSERT INTO family_access (family_id, user_id, access_level, status)
    VALUES (1, 7, 'OWNER', 'ACTIVE');
    """)

    persons = [
        (1, 'per-rajesh-001', 'RY-PER-2026-000001', 'Rajesh Patil', '1984-05-15', 'MALE', 'ADULT', '5ft 9in', '72 kg', 'Black', 'Brown', 'Wheatish', 'Mole on right forearm', 0, 0, 0, 'or', 'PRIVATE', 'ACTIVE'),
        (2, 'per-sneha-002', 'RY-PER-2026-000002', 'Sneha Patil', '1988-08-20', 'FEMALE', 'ADULT', '5ft 4in', '60 kg', 'Dark Brown', 'Brown', 'Fair', 'Small scar on chin', 0, 0, 0, 'or', 'PRIVATE', 'ACTIVE'),
        (3, 'per-aarav-003', 'RY-PER-2026-000003', 'Aarav Patil', '2018-03-10', 'MALE', 'CHILD', '4ft 1in', '26 kg', 'Black', 'Dark Brown', 'Fair', 'Birthmark on left shoulder', 0, 0, 0, 'or', 'PRIVATE', 'ACTIVE'),
        (4, 'per-sunita-004', 'RY-PER-2026-000004', 'Sunita Patil', '1959-11-04', 'FEMALE', 'ELDERLY', '5ft 1in', '55 kg', 'Grey/White', 'Brown', 'Wheatish', 'Surgical scar on right knee', 1, 1, 1, 'or', 'PRIVATE', 'ACTIVE')
    ]
    cursor.executemany("""
    INSERT INTO person_profiles (id, uuid, person_code, full_name, date_of_birth, gender, age_category, height, approx_weight, hair_color, eye_color, skin_tone, identification_mark, glasses, hearing_aid, walking_assistance, preferred_language, profile_visibility, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, persons)

    f_members = [
        (1, 'fm-001', 1, 1, 'Father', 'ACTIVE'),
        (2, 'fm-002', 1, 2, 'Mother', 'ACTIVE'),
        (3, 'fm-003', 1, 3, 'Son', 'ACTIVE'),
        (4, 'fm-004', 1, 4, 'Grandmother', 'ACTIVE')
    ]
    cursor.executemany("""
    INSERT INTO family_members (id, uuid, family_id, person_id, relationship_type, status)
    VALUES (?, ?, ?, ?, ?, ?);
    """, f_members)

    clothings = [
        (1, 'Kurta', 'White', 'Pajama', 'White', 'Leather Sandals', 'Brown', 'None', 'Wrist Watch', 'Traditional pilgrim attire'),
        (2, 'Saree', 'Yellow/Gold', 'Petticoat', 'Yellow', 'Chappals', 'Red', 'Dupatta', 'Gold Bangle', 'Silk festival saree'),
        (3, 'T-Shirt', 'Bright Red', 'Shorts', 'Navy Blue', 'Sneakers', 'Blue', 'Cap', 'Yellow wristband', 'Spiderman logo red t-shirt'),
        (4, 'Saree', 'Cotton Blue', 'Petticoat', 'Blue', 'Soft Orthopedic Shoes', 'Black', 'Shawl', 'Spectacles & Cane', 'Light blue cotton saree with walking stick')
    ]
    cursor.executemany("""
    INSERT INTO clothing_profiles (person_id, top_type, top_color, bottom_type, bottom_color, footwear, footwear_color, headwear, accessories, description)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, clothings)

    safeties = [
        (3, 'Mild Asthma', 'Inhaler in backpack', 'Dust allergy', 'O+', 'None', 'Speaks Odia/Hindi', 0, 1),
        (4, 'Hypertension & Arthritis', 'Daily BP tablets morning/night', 'Penicillin allergy', 'B+', 'Uses walking stick', 'Hard of hearing in left ear', 1, 1)
    ]
    cursor.executemany("""
    INSERT INTO person_safety_profiles (person_id, medical_condition, medication_requirement, allergy_information, blood_group, mobility_assistance, communication_difficulty, cognitive_assistance_required, consent_status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, safeties)

    emergencies = [
        (1, 'Amit Patil', 'Brother', '9988776655', '9988776654', 1),
        (2, 'Rajesh Patil', 'Spouse', '9876543216', None, 1),
        (3, 'Rajesh Patil', 'Father', '9876543216', '9988776655', 1),
        (4, 'Rajesh Patil', 'Son', '9876543216', '9988776655', 1)
    ]
    cursor.executemany("""
    INSERT INTO emergency_contacts (person_id, contact_name, relationship, mobile, alternate_mobile, is_primary)
    VALUES (?, ?, ?, ?, ?, ?);
    """, emergencies)
    seed_module3_sqlite(cursor)

def seed_module3_sqlite(cursor):
    facilities = [
        (1, 'fac-001', 'WS-FAC-001', 'Alandi Temple First Aid Center', 'FIRST_AID_CENTER', 'Alandi', 18.6773000, 73.8967000, '02027180001', 60, 12, 'AVAILABLE'),
        (2, 'fac-002', 'WS-FAC-002', 'Pune Wari Emergency Center', 'EMERGENCY_CENTER', 'Pune Route', 18.5204000, 73.8567000, '02026120002', 150, 45, 'AVAILABLE'),
        (3, 'fac-003', 'WS-FAC-003', 'Saswad Wari Medical Camp 12', 'MEDICAL_CAMP', 'Saswad', 18.3444000, 74.0306000, '02115222003', 100, 72, 'AVAILABLE'),
        (4, 'fac-004', 'WS-FAC-004', 'Jejuri Temple Health Booth', 'FIRST_AID_CENTER', 'Jejuri', 18.2747000, 74.1578000, '02115253004', 50, 48, 'BUSY'),
        (5, 'fac-005', 'WS-FAC-005', 'Lonand Dindi Medical Base', 'MEDICAL_CAMP', 'Lonand', 18.0400000, 74.1900000, '02169224005', 80, 20, 'AVAILABLE'),
        (6, 'fac-006', 'WS-FAC-006', 'Pandharpur Vitthal General Hospital', 'HOSPITAL', 'Pandharpur', 17.6775000, 75.3278000, '02186223006', 200, 110, 'AVAILABLE')
    ]
    cursor.executemany("""
    INSERT INTO medical_facilities (id, uuid, facility_code, name, facility_type, zone, latitude, longitude, contact_number, capacity, current_patients, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, facilities)

    services = [
        (1, 'First Aid', 1), (1, 'Dehydration Treatment', 1), (1, 'Wound Care', 1),
        (2, 'Emergency Treatment', 1), (2, 'Cardiac Support', 1), (2, 'Ambulance Support', 1), (2, 'Pharmacy', 1),
        (3, 'First Aid', 1), (3, 'Dehydration Treatment', 1), (3, 'Orthopedic Support', 1), (3, 'Pharmacy', 1),
        (4, 'First Aid', 1), (4, 'Wound Care', 1),
        (5, 'Dehydration Treatment', 1), (5, 'Orthopedic Support', 1), (5, 'First Aid', 1),
        (6, 'Emergency Treatment', 1), (6, 'Cardiac Support', 1), (6, 'Orthopedic Support', 1), (6, 'Pharmacy', 1)
    ]
    cursor.executemany("""
    INSERT INTO medical_facility_services (facility_id, service_name, available)
    VALUES (?, ?, ?);
    """, services)

    cursor.execute("""
    INSERT INTO medical_staff (id, uuid, user_id, staff_code, staff_role, qualification, specialization, facility_id, shift_start, shift_end, status)
    VALUES (1, 'stf-001', 5, 'WS-STF-001', 'DOCTOR', 'MBBS, MD', 'Emergency Medicine & Trauma', 3, '08:00', '20:00', 'ON_DUTY');
    """)

    ambulances = [
        (1, 'amb-101', 'WS-AMB-101', 'MH-12-PA-1001', 'ADVANCED_LIFE_SUPPORT', 'Santosh Pawar', '9822001122', 18.3450000, 74.0310000, 'AVAILABLE', 'Defibrillator, Oxygen Cylinder, Ventilator, Stretcher'),
        (2, 'amb-102', 'WS-AMB-102', 'MH-12-PA-1002', 'BASIC_LIFE_SUPPORT', 'Ganesh Jadhav', '9822001123', 18.5210000, 73.8570000, 'AVAILABLE', 'First Aid Kit, Oxygen Mask, Stretcher'),
        (3, 'amb-103', 'WS-AMB-103', 'MH-14-BT-2005', 'PATIENT_TRANSPORT', 'Anil Shinde', '9822001124', 18.0410000, 74.1910000, 'AVAILABLE', 'Basic First Aid & Stretcher')
    ]
    cursor.executemany("""
    INSERT INTO ambulances (id, uuid, ambulance_code, registration_number, ambulance_type, driver_name, driver_contact, latitude, longitude, status, equipment_description)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, ambulances)

    cases = [
        (1, 'mc-001', 'WS-MED-2026-000001', 4, None, None, None, None, None, 7, 'BREATHING_DIFFICULTY', 'HIGH', 85, 'CRITICAL', 'Breathing difficulty (+35), Elderly (+15), Hypertension (+20), Route (+10)', 'Grandmother Sunita Patil experiencing breathing tightness near Saswad halt.', 'TRIAGE'),
        (2, 'mc-002', 'WS-MED-2026-000002', 3, None, None, None, None, None, 7, 'DEHYDRATION', 'MEDIUM', 35, 'MEDIUM', 'Dehydration (+20), Child (+15)', 'Aarav Patil showing signs of fatigue and mild fever.', 'REPORTED'),
        (3, 'mc-003', 'WS-MED-2026-000003', None, 'TEMP-PAT-2026-00001', 'Unidentified Warkari', 55, 'MALE', 'Male warkari in white kurta found unconscious.', 6, 'FAINTING', 'CRITICAL', 85, 'CRITICAL', 'Unconscious (+40), Fatigue (+20), Unidentified (+15)', 'Unconscious pilgrim collapsed on road during heat.', 'ASSIGNED')
    ]
    cursor.executemany("""
    INSERT INTO medical_cases (id, uuid, case_number, patient_person_id, temp_patient_code, temp_patient_name, temp_patient_age, temp_patient_gender, temp_patient_description, reported_by_user_id, emergency_type, reported_severity, priority_score, priority_level, priority_reasons, description, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, cases)

    locations = [
        (1, 'Saswad', 'Alandi-Pandharpur Dindi Route', 'Near Saswad Palkhi Halt Tent 4', 18.3444000, 74.0306000, 'Behind Palkhi Pavilion', 'GPS'),
        (2, 'Saswad', 'Alandi-Pandharpur Dindi Route', 'Saswad Rest Stop Kiosk', 18.3450000, 74.0320000, 'Near Water Dispenser 3', 'MANUAL'),
        (3, 'Lonand', 'Pune-Pandharpur Highway', 'Pargaon Bridge Crossing', 18.0400000, 74.1900000, 'Right shoulder of main road', 'VOLUNTEER')
    ]
    cursor.executemany("""
    INSERT INTO medical_case_locations (case_id, zone, route, landmark, latitude, longitude, location_description, location_source)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, locations)

    symptoms = [
        (1, 'Difficulty breathing', 'HIGH'), (1, 'Chest tightness', 'HIGH'),
        (2, 'Dizziness', 'MODERATE'), (2, 'Dehydration', 'MODERATE'),
        (3, 'Unconsciousness', 'CRITICAL'), (3, 'Fever', 'HIGH')
    ]
    cursor.executemany("""
    INSERT INTO medical_case_symptoms (case_id, symptom, severity)
    VALUES (?, ?, ?);
    """, symptoms)
    seed_module4_sqlite(cursor)

def seed_module4_sqlite(cursor):
    cases = [
        (1, 'lp-001', 'WS-LP-2026-000001', 3, None, None, None, None, None, 1, None, 7, 'Father', 85, 'CRITICAL', 'Child (+30), Crowded route (+10), Night (+10), Asthma (+25), Red shirt (+10)', 'SEARCHING', 'Aarav went missing near Saswad Rest Stop Water Tank 3.'),
        (2, 'lp-002', 'WS-LP-2026-000002', 4, None, None, None, None, None, 1, None, 7, 'Son', 60, 'HIGH', 'Elderly 60+ (+25), Medical requirement (+25), Disappeared in crowd (+10)', 'REPORTED', 'Sunita Patil separated near Jejuri Temple steps.'),
        (3, 'lp-003', 'WS-LP-2026-000003', None, 'TEMP-PER-2026-00001', 'Unregistered Boy', 6, 'MALE', 'Child in green t-shirt', None, None, 6, 'Volunteer Report', 80, 'CRITICAL', 'Child (+30), Non-verbal (+20), Unregistered (+15), High-density (+15)', 'UNDER_REVIEW', 'Child found wandering near Lonand.')
    ]

    cursor.executemany("""
    INSERT INTO lost_person_cases (id, uuid, case_number, person_id, temp_person_code, temp_person_name, temp_person_age, temp_person_gender, temp_person_description, family_id, dindi_id, reported_by_user_id, reporter_relationship, priority_score, priority_level, priority_reasons, status, additional_information, last_seen_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'));
    """, cases)

    locations = [
        (1, 'Saswad', 'Alandi-Pandharpur Dindi Route', 'Saswad Rest Stop Water Tank 3', 18.3450000, 74.0320000, 'Behind Water Dispenser 3', 'MANUAL'),
        (2, 'Jejuri', 'Alandi-Pandharpur Dindi Route', 'Jejuri Temple Main Steps', 18.2747000, 74.1578000, 'Near Deepastambha entrance', 'MANUAL'),
        (3, 'Lonand', 'Alandi-Pandharpur Dindi Route', 'Lonand Palkhi Pavilion Stage 2', 18.0400000, 74.1900000, 'Near Annachhatra Distribution Center', 'VOLUNTEER')
    ]
    cursor.executemany("""
    INSERT INTO lost_person_locations (case_id, zone, route_section, landmark, latitude, longitude, location_description, location_source)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, locations)

    clothing = [
        (1, 'T-Shirt', 'Bright Red with Spiderman', 'Shorts', 'Navy Blue', 'Sneakers', 'Blue', 'Yellow Cap', 'Yellow Safety Wristband', 'Carrying small blue backpack', 1),
        (2, 'Saree', 'Cotton Blue', 'Pajama', 'White', 'Sandals', 'Brown', 'Saree Pallu', 'Gold bangles', 'Walking cane in hand', 1),
        (3, 'T-Shirt', 'Green', 'Pants', 'Black', 'Slippers', 'Black', 'None', 'Red string on wrist', 'Green printed t-shirt', 0)
    ]
    cursor.executemany("""
    INSERT INTO lost_person_clothing (case_id, top_type, top_color, bottom_type, bottom_color, footwear, footwear_color, headwear, accessories, description, confirmed_from_profile)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, clothing)

    notes = [
        (1, 7, 'Checked water tank area with volunteers. Moving toward Saswad Help Center No. 2.', 'FAMILY_VISIBLE'),
        (1, 4, 'Help center announced missing report on loudspeaker in Zone 4.', 'INTERNAL')
    ]
    cursor.executemany("""
    INSERT INTO lost_person_notes (case_id, created_by, note, visibility)
    VALUES (?, ?, ?, ?);
    """, notes)
    seed_module5_sqlite(cursor)

def seed_module5_sqlite(cursor):
    cases = [
        (1, 'fp-001', 'WS-FP-2026-000001', 'TEMP-FP-PER-2026-00001', 3, 6, 'IDENTIFIED_PERSON', 'Aarav Patil', 8, 'MALE', 'Marathi', 'CAN_COMMUNICATE', 0, 'Rest & Water', None, 'VERIFICATION'),
        (2, 'fp-002', 'WS-FP-2026-000002', 'TEMP-FP-PER-2026-00002', 4, 4, 'PARTIALLY_IDENTIFIED_PERSON', 'Sunita Patil', 67, 'FEMALE', 'Marathi', 'LIMITED_COMMUNICATION', 1, 'Medication check', None, 'FAMILY_CONTACTED'),
        (3, 'fp-003', 'WS-FP-2026-000003', 'TEMP-FP-PER-2026-00003', None, 6, 'UNIDENTIFIED_PERSON', 'Unidentified Pilgrim', 65, 'MALE', 'Kannada', 'CANNOT_COMMUNICATE', 0, 'Interpreter & Wheelchair', None, 'REPORTED')
    ]
    cursor.executemany("""
    INSERT INTO found_person_cases (id, uuid, case_number, temporary_person_id, linked_person_id, reported_by_user_id, identification_status, approximate_name, approximate_age, gender, language, communication_status, medical_attention_required, special_assistance_required, dindi_id, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, cases)

    locations = [
        (1, 'Saswad', 'Alandi-Pandharpur Dindi Route', 'Saswad Help Center No. 2', 18.3460000, 74.0330000, 'Found sitting near Saswad Help Center 2', 'VOLUNTEER'),
        (2, 'Jejuri', 'Alandi-Pandharpur Dindi Route', 'Jejuri Temple Arch', 18.2750000, 74.1580000, 'Spotted resting near temple gate by police patrol', 'POLICE'),
        (3, 'Lonand', 'Alandi-Pandharpur Dindi Route', 'Lonand Palkhi Pavilion Stage 2', 18.0410000, 74.1910000, 'Found sitting alone near Annachhatra', 'VOLUNTEER')
    ]
    cursor.executemany("""
    INSERT INTO found_person_locations (case_id, zone, route_section, landmark, latitude, longitude, location_description, location_source)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, locations)

    clothing = [
        (1, 'T-Shirt', 'Red', 'Shorts', 'Navy Blue', 'Sneakers', 'Blue', 'Yellow Cap', 'Yellow Safety Wristband', 'Spiderman printed red shirt', 'HIGH'),
        (2, 'Saree', 'Blue', 'Pajama', 'White', 'Sandals', 'Brown', 'Saree Pallu', 'Gold bangles', 'Cotton blue saree', 'HIGH'),
        (3, 'Kurta', 'White', 'Pyjama', 'White', 'Slippers', 'Black', 'Gandhi Cap', 'Tulsi mala', 'Elderly pilgrim in traditional dhoti kurta', 'MEDIUM')
    ]
    cursor.executemany("""
    INSERT INTO found_person_clothing (case_id, top_type, top_color, bottom_type, bottom_color, footwear, footwear_color, headwear, accessories, description, confidence_level)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, clothing)

    safe_locs = [
        (1, 'HELP_CENTER', 2, 'Saswad Help Center No. 2', 'AT_HELP_CENTER'),
        (2, 'POLICE_POST', 1, 'Jejuri Police Control Post 1', 'AT_POLICE_POST'),
        (3, 'HELP_CENTER', 1, 'Lonand Help Center No. 1', 'AT_HELP_CENTER')
    ]
    cursor.executemany("""
    INSERT INTO found_person_safe_locations (case_id, facility_type, facility_id, location_name, status)
    VALUES (?, ?, ?, ?, ?);
    """, safe_locs)

    clues = [
        (1, 'NAME', 'Aarav Patil', 'Verbal statement', 'HIGH', 1),
        (1, 'DINDI_NUMBER', 'Dindi 27', 'Verbal statement', 'HIGH', 1),
        (2, 'FAMILY_NAME', 'Patil Family of Pune', 'Verbal statement', 'MEDIUM', 0),
        (3, 'VILLAGE', 'Belagavi Village', 'Verbal statement', 'LOW', 0)
    ]
    cursor.executemany("""
    INSERT INTO found_person_identification_clues (case_id, clue_type, clue_value, source, confidence, verified)
    VALUES (?, ?, ?, ?, ?, ?);
    """, clues)

    notes = [
        (1, 6, 'Aarav is safe and resting at Saswad Help Center 2. Biscuits and water provided.', 'FAMILY_VISIBLE'),
        (2, 4, 'Sunita Patil resting at Jejuri Police Post. Family contact attempt in progress.', 'INTERNAL')
    ]
    cursor.executemany("""
    INSERT INTO found_person_notes (case_id, created_by, note, visibility)
    VALUES (?, ?, ?, ?);
    """, notes)
    seed_module6_sqlite(cursor)

def seed_module6_sqlite(cursor):
    storage = [
        (1, 'Saswad Help Center Storage Tent 2', 'FAC-SAS-02', 'Locker B-12', 'Shelf 3', 50, 1, 'AVAILABLE'),
        (2, 'Jejuri Police Post Locker Desk', 'FAC-JEJ-01', 'Cabinet A-04', 'Shelf 1', 30, 0, 'AVAILABLE')
    ]
    cursor.executemany("""
    INSERT INTO item_storage_locations (id, facility_name, facility_code, locker, shelf, capacity, current_count, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, storage)

    lost_items = [
        (1, 'li-001', 'WS-LI-2026-000001', 7, 'MOBILE_PHONE', 'Samsung Galaxy A54', 'Samsung', 'Galaxy A54 5G', 'Black', 'Black phone in blue cover', 25000.0, 'SN-SAMS-998811', '354892019283741', 'REPORTED', None),
        (2, 'li-002', 'WS-LI-2026-000002', 7, 'WALLET', 'Leather Brown Wallet', 'Titan', 'Classic', 'Brown', 'Leather wallet with Aadhaar card', 1500.0, None, None, 'REPORTED', None)
    ]
    cursor.executemany("""
    INSERT INTO lost_item_cases (id, uuid, case_number, reported_by_user_id, item_category, item_name, brand, model, color, description, approximate_value, serial_number, imei, status, dindi_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, lost_items)

    found_items = [
        (1, 'fi-001', 'WS-FI-2026-000001', 6, 'MOBILE_PHONE', 'Black Smartphone in Blue Cover', 'Samsung', 'Galaxy Series', 'Black', 'Found near Saswad halt water dispenser', 'GOOD', None, 6, 'STORED')
    ]
    cursor.executemany("""
    INSERT INTO found_item_cases (id, uuid, case_number, reported_by_user_id, item_category, item_name, brand, model, color, description, condition, dindi_id, found_by_user_id, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, found_items)

    locations = [
        (1, None, 'Saswad', 'Alandi-Pandharpur Route', 'Saswad Halt Water Dispenser 3', 18.345, 74.032, 'LOST', 'Dropped near water dispenser'),
        (None, 1, 'Saswad', 'Alandi-Pandharpur Route', 'Saswad Halt Water Dispenser 3', 18.345, 74.032, 'FOUND', 'Picked up by volunteer team')
    ]
    cursor.executemany("""
    INSERT INTO item_locations (lost_item_case_id, found_item_case_id, zone, route_section, landmark, latitude, longitude, location_type, location_description)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, locations)

    claims = [
        (1, 'CLM-2026-000001', 1, 7, 'This is my Samsung Galaxy A54 phone.', 'SUBMITTED')
    ]
    cursor.executemany("""
    INSERT INTO item_claims (id, claim_number, found_item_case_id, claimed_by_user_id, claim_description, status)
    VALUES (?, ?, ?, ?, ?, ?);
    """, claims)

    custody = [
        (1, 6, 6, 'Saswad Halt Water Dispenser 3', 'Saswad Help Center Storage Tent 2', 'STORED', 'Stored in Locker B-12')
    ]
    cursor.executemany("""
    INSERT INTO item_custody_history (found_item_case_id, from_user_id, to_user_id, from_location, to_location, action, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """, custody)
    seed_module7_sqlite(cursor)

def seed_module7_sqlite(cursor):
    ai_matches = [
        (1, 'aim-001', 'PERSON', 1, 1, 92, 88, 90, '{"reasons": ["✓ Similar estimated age (8 vs 8 years)", "✓ Same gender (Male)", "✓ Matching clothing (Red T-shirt & Navy shorts)", "✓ Nearby location (Saswad route halt)", "✓ Timestamp within 1 hour"], "factors": {"age": 95, "clothing": 95, "location": 90, "time": 90}}', 'v1.0-Hybrid', 'GENERATED'),
        (2, 'aim-002', 'ITEM', 1, 1, 94, 90, 85, '{"reasons": ["✓ Same category (Mobile Phone)", "✓ Matching brand & series (Samsung Galaxy)", "✓ Matching color (Black)", "✓ Matching cover (Blue silicon)", "✓ Nearby lost & found spot (Saswad Water Dispenser 3)"], "factors": {"category": 100, "brand": 95, "color": 100, "location": 90}}', 'v1.0-Hybrid', 'GENERATED')
    ]
    cursor.executemany("""
    INSERT INTO ai_match_results (id, uuid, match_type, source_case_id, candidate_case_id, match_score, confidence_score, data_quality_score, explanation, model_version, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, ai_matches)
    seed_module8_sqlite(cursor)

def seed_module8_sqlite(cursor):
    dindis = [
        (1, 'din-027', 'WS-DIN-2026-000027', 27, 'Shree Sant Tukaram Maharaj Dindi No. 27', 'Official registered Warkari Dindi travelling Alandi-Pandharpur route', 2026, 'Alandi', 'Pandharpur', 250, 'VERIFIED', 1),
        (2, 'din-015', 'WS-DIN-2026-000015', 15, 'Shree Dnyaneshwar Maharaj Dindi No. 15', 'Registered Warkari group travelling Pune to Pandharpur', 2026, 'Pune', 'Pandharpur', 180, 'VERIFIED', 1)
    ]
    cursor.executemany("""
    INSERT INTO dindis (id, uuid, dindi_code, dindi_number, name, description, registration_year, start_location, destination, expected_member_count, status, created_by)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, dindis)

    leaders = [
        (1, 1, 4, 5, 'PRIMARY_LEADER', None, None, 'ACTIVE'),
        (2, 2, None, 6, 'PRIMARY_LEADER', None, None, 'ACTIVE')
    ]
    cursor.executemany("""
    INSERT INTO dindi_leaders (id, dindi_id, person_id, user_id, role, start_date, end_date, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, leaders)

    memberships = [
        (1, 1, 'MEM-DIN27-001', 'MEMBER', 'ACTIVE'),
        (1, 2, 'MEM-DIN27-002', 'MEMBER', 'ACTIVE'),
        (1, 3, 'MEM-DIN27-003', 'MEMBER', 'ACTIVE'),
        (1, 4, 'MEM-DIN27-004', 'LEADER', 'ACTIVE')
    ]
    cursor.executemany("""
    INSERT INTO dindi_memberships (dindi_id, person_id, membership_number, role, status)
    VALUES (?, ?, ?, ?, ?);
    """, memberships)

    schedules = [
        (1, '2026-07-01', 'Alandi', 'Pune', '05:30 AM', '06:00 PM', 'Phugewadi Rest Tent', 'Day 1 march towards Pune city halt', 'SCHEDULED'),
        (1, '2026-07-02', 'Pune', 'Saswad', '05:00 AM', '06:30 PM', 'Dive Ghat Halt Desk', 'Ascent via Dive Ghat pass', 'SCHEDULED'),
        (1, '2026-07-03', 'Saswad', 'Jejuri', '06:00 AM', '05:00 PM', 'Saswad Water Dispenser 3', 'Tea halt at Saswad water station', 'SCHEDULED')
    ]
    cursor.executemany("""
    INSERT INTO dindi_schedules (dindi_id, schedule_date, start_location, end_location, expected_start_time, expected_arrival_time, rest_point, notes, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, schedules)

    announcements = [
        (1, 'Morning Palkhi Departure Time', 'Dindi march will assemble at 05:15 AM near Saswad Halt Water Station. Please form rows.', 'IMPORTANT', 5, 'ACTIVE')
    ]
    cursor.executemany("""
    INSERT INTO dindi_announcements (dindi_id, title, message, priority, created_by, status)
    VALUES (?, ?, ?, ?, ?, ?);
    """, announcements)

    contacts = [
        (1, 'PRIMARY', 'Mr. Dindi Leader', '+91 98220 99999', 'PUBLIC'),
        (1, 'EMERGENCY', 'Dindi Medical & Helpline Desk', '+91 98220 88888', 'PUBLIC')
    ]
    cursor.executemany("""
    INSERT INTO dindi_contacts (dindi_id, contact_type, contact_name, contact_number, visibility)
    VALUES (?, ?, ?, ?, ?);
    """, contacts)
    seed_module9_sqlite(cursor)

def seed_module9_sqlite(cursor):
    routes = [
        (1, 'route-001', 'WS-ROUTE-2026-000001', 'Alandi–Pandharpur Palkhi Route', 'Alandi', 'Pandharpur', 242.50, 'ACTIVE')
    ]
    cursor.executemany("""
    INSERT INTO wari_routes (id, uuid, route_code, name, start_location, destination, total_distance, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, routes)

    sections = [
        (1, 1, 'SEC-01', 1, 'Alandi', 'Pune', 22.00, '1 Day', 'ACTIVE'),
        (2, 1, 'SEC-02', 2, 'Pune', 'Saswad', 32.00, '1 Day', 'ACTIVE'),
        (3, 1, 'SEC-03', 3, 'Saswad', 'Jejuri', 16.00, '1 Day', 'ACTIVE'),
        (4, 1, 'SEC-04', 4, 'Jejuri', 'Lonand', 22.00, '1 Day', 'ACTIVE'),
        (5, 1, 'SEC-05', 5, 'Lonand', 'Phaltan', 32.00, '1 Day', 'ACTIVE'),
        (6, 1, 'SEC-06', 6, 'Phaltan', 'Malshiras', 48.00, '2 Days', 'ACTIVE'),
        (7, 1, 'SEC-07', 7, 'Malshiras', 'Pandharpur', 70.50, '2 Days', 'ACTIVE')
    ]
    cursor.executemany("""
    INSERT INTO route_sections (id, route_id, section_code, sequence_number, start_location, end_location, distance_km, estimated_duration, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, sections)

    locations = [
        (1, 'loc-med-01', 'Saswad Route Medical Camp 1', 'MEDICAL_CAMP', 3, 'Saswad', 18.3450000, 74.0320000, '24/7 First-aid emergency medical tent near Saswad water station', '+91 98220 11111', 'OPEN'),
        (2, 'loc-hc-01', 'Saswad Help Center Kiosk 2', 'HELP_CENTER', 3, 'Saswad', 18.3440000, 74.0310000, 'Kiosk desk for lost person & item inquiries', '+91 98220 22222', 'OPEN'),
        (3, 'loc-rest-01', 'Saswad Water Dispenser & Rest Spot 3', 'WATER_POINT', 3, 'Saswad', 18.3460000, 74.0330000, 'Pilgrim drinking water dispensers and rest shade', '+91 98220 33333', 'OPEN'),
        (4, 'loc-cp-01', 'Saswad Route Checkpoint 3', 'HELP_CENTER', 3, 'Saswad', 18.3455000, 74.0325000, 'Official Palkhi passage check-in desk', '+91 98220 44444', 'OPEN')
    ]
    cursor.executemany("""
    INSERT INTO wari_locations (id, uuid, name, location_type, route_section_id, zone, latitude, longitude, description, contact_number, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, locations)

    crowd = [
        (1, 'Z-SAS-01', 'Saswad Dive Ghat Ascent Zone', 2, 'MODERATE', 1)
    ]
    cursor.executemany("""
    INSERT INTO crowd_zones (id, zone_code, zone_name, route_section_id, crowd_level, updated_by)
    VALUES (?, ?, ?, ?, ?, ?);
    """, crowd)

    dindi_locs = [
        (1, 18.3450000, 74.0320000, 12.5, 'GPS', 'MOVING', 5)
    ]
    cursor.executemany("""
    INSERT INTO dindi_location_updates (dindi_id, latitude, longitude, accuracy, location_source, status, recorded_by)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """, dindi_locs)

    checkins = [
        (1, 4, 5, 18.3455000, 74.0325000, 'PASSED')
    ]
    cursor.executemany("""
    INSERT INTO dindi_checkins (dindi_id, checkpoint_id, checked_in_by, latitude, longitude, status)
    VALUES (?, ?, ?, ?, ?, ?);
    """, checkins)
    seed_module10_sqlite(cursor)

def seed_module10_sqlite(cursor):
    volunteers = [
        (1, 'vol-001', 'WS-VOL-2026-000001', 6, 1, 'ACTIVE', 'VERIFIED', 3, 'Saswad', '+91 98220 99001'),
        (2, 'vol-002', 'WS-VOL-2026-000002', 8, None, 'ACTIVE', 'VERIFIED', 1, 'Saswad', '+91 98220 99002')
    ]
    cursor.executemany("""
    INSERT INTO volunteers (id, uuid, volunteer_code, user_id, person_id, status, verification_status, experience_years, preferred_zone, emergency_contact)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, volunteers)

    skills = [
        (1, 'FIRST_AID', 'CERTIFIED', 1, 1),
        (1, 'CROWD_MANAGEMENT', 'ADVANCED', 1, 1),
        (1, 'CHILD_ASSISTANCE', 'ADVANCED', 1, 1),
        (2, 'LANGUAGE_SUPPORT', 'INTERMEDIATE', 1, 1)
    ]
    cursor.executemany("""
    INSERT INTO volunteer_skills (volunteer_id, skill_name, skill_level, verified, verified_by)
    VALUES (?, ?, ?, ?, ?);
    """, skills)

    languages = [
        (1, 'Marathi', 'NATIVE'),
        (1, 'Hindi', 'ADVANCED'),
        (1, 'English', 'INTERMEDIATE'),
        (2, 'Odia', 'NATIVE')
    ]
    cursor.executemany("""
    INSERT INTO volunteer_languages (volunteer_id, language, proficiency)
    VALUES (?, ?, ?);
    """, languages)

    shifts = [
        (1, 'SHIFT-MNG-01', 'Morning Shift (06:00 - 14:00)', '06:00', '14:00', 'Saswad', 'ACTIVE'),
        (2, 'SHIFT-AFT-02', 'Afternoon Shift (14:00 - 22:00)', '14:00', '22:00', 'Saswad', 'ACTIVE')
    ]
    cursor.executemany("""
    INSERT INTO volunteer_shifts (id, shift_code, name, start_time, end_time, zone, status)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """, shifts)

    teams = [
        (1, 'TEAM-MED-01', 'Saswad First Aid Response Team', 'MEDICAL', 1, 'Saswad', 'ACTIVE')
    ]
    cursor.executemany("""
    INSERT INTO volunteer_teams (id, team_code, name, team_type, leader_id, zone, status)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """, teams)

    members = [
        (1, 1, 'LEADER', 'ACTIVE'),
        (1, 2, 'MEMBER', 'ACTIVE')
    ]
    cursor.executemany("""
    INSERT INTO volunteer_team_members (team_id, volunteer_id, role, status)
    VALUES (?, ?, ?, ?);
    """, members)

    tasks = [
        (1, 'task-001', 'WS-TASK-2026-000001', 'Lost Child Search Assistance near Saswad Water Station', 'Assist help center operator in searching for missing child Aarav near Saswad Rest Spot 3', 'LOST_PERSON_SEARCH', 'HIGH', 'MODULE_4', 'WS-LP-2026-000001', 'Saswad', 'Pune -> Saswad', 18.3450000, 74.0320000, 'UNASSIGNED', 1)
    ]
    cursor.executemany("""
    INSERT INTO volunteer_tasks (id, uuid, task_code, title, description, task_type, priority, source_module, source_case_id, zone, route_section, latitude, longitude, status, created_by)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, tasks)

    reqs = [
        (1, 'CHILD_ASSISTANCE', 'INTERMEDIATE', 'Marathi', 1)
    ]
    cursor.executemany("""
    INSERT INTO volunteer_task_requirements (task_id, required_skill, minimum_skill_level, required_language, quantity)
    VALUES (?, ?, ?, ?, ?);
    """, reqs)










def execute_query(query, params=(), fetchone=False, fetchall=False, commit=False):
    """
    Abstraction layer executing SQL query against MySQL or SQLite transparently.
    Handles placeholder translation (%s vs ?) and function translation (NOW() vs datetime('now')) automatically.
    """
    conn, db_type = get_db_connection()
    try:
        if db_type == 'sqlite':
            # Translate MySQL placeholders and functions to SQLite equivalents
            query_sqlite = query.replace('%s', '?').replace('NOW()', "datetime('now')").replace('now()', "datetime('now')")
            cursor = conn.cursor()
            cursor.execute(query_sqlite, params)

            
            if commit:
                conn.commit()
                last_id = cursor.lastrowid
                conn.close()
                return last_id
            
            if fetchone:
                row = cursor.fetchone()
                conn.close()
                return dict(row) if row else None
            
            if fetchall:
                rows = cursor.fetchall()
                conn.close()
                return [dict(r) for r in rows]
            
            conn.close()
            return cursor.rowcount
        else:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                if commit:
                    conn.commit()
                    last_id = cursor.lastrowid
                    conn.close()
                    return last_id
                
                if fetchone:
                    res = cursor.fetchone()
                    conn.close()
                    return res
                
                if fetchall:
                    res = cursor.fetchall()
                    conn.close()
                    return res
                
                conn.close()
                return cursor.rowcount
    except Exception as e:
        if conn:
            conn.close()
        raise e

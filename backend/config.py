import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'reuniteai-super-secret-jwt-key-2026-puri-rath-yatra')
    
    # Session / JWT configuration
    SESSION_DURATION = timedelta(hours=24)
    PASSWORD_RESET_TOKEN_DURATION = timedelta(hours=1)
    
    # Database Configuration (MySQL 8+)
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'reuniteai')
    
    # SQLite Fallback for Instant Zero-Dependency Run/Testing if MySQL is inactive
    SQLITE_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'reuniteai_local.db')
    
    # Static & Upload Configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'assets', 'images', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB Max upload

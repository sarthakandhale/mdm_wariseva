import os
import uuid
from datetime import datetime
from db import execute_query
from services.audit_service import log_audit_event

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_person_photo(person_id, file_obj, current_user):
    """
    Saves an uploaded image file for a person profile.
    """
    if not file_obj or not file_obj.filename:
        return False, {"message": "No photo file provided.", "error_code": "NO_FILE"}, 400

    if not allowed_file(file_obj.filename):
        return False, {"message": "Invalid file format. Allowed formats: JPG, JPEG, PNG.", "error_code": "INVALID_FORMAT"}, 400

    file_bytes = file_obj.read()
    file_size = len(file_bytes)
    if file_size > MAX_FILE_SIZE:
        return False, {"message": "File size exceeds 5MB limit.", "error_code": "FILE_TOO_LARGE"}, 400

    ext = file_obj.filename.rsplit('.', 1)[1].lower()
    unique_filename = f"photo_{person_id}_{uuid.uuid4().hex[:10]}_{int(datetime.now().timestamp())}.{ext}"

    # Directory path
    upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'assets', 'images', 'uploads', 'person_photos'))
    os.makedirs(upload_dir, exist_ok=True)

    file_path_full = os.path.join(upload_dir, unique_filename)
    with open(file_path_full, 'wb') as f:
        f.write(file_bytes)

    relative_url = f"/assets/images/uploads/person_photos/{unique_filename}"
    photo_uuid = f"pho-{uuid.uuid4().hex[:12]}"

    # Reset existing primary photos if setting primary
    execute_query("UPDATE person_photos SET is_primary = 0 WHERE person_id = %s", (person_id,), commit=True)

    photo_id = execute_query("""
    INSERT INTO person_photos (uuid, person_id, file_path, file_type, file_size, is_primary, uploaded_by, created_at)
    VALUES (%s, %s, %s, %s, %s, 1, %s, NOW())
    """, (photo_uuid, person_id, relative_url, ext, file_size, current_user['user_id']), commit=True)

    log_audit_event(
        user_id=current_user['user_id'],
        action="PHOTO_UPLOADED",
        details={"person_id": person_id, "photo_id": photo_id, "file_path": relative_url}
    )

    return True, {
        "photo_id": photo_id,
        "file_path": relative_url,
        "file_size": file_size,
        "is_primary": 1
    }, 201

def delete_person_photo(person_id, photo_id, current_user):
    """
    Deletes photo record and associated physical file.
    """
    photo = execute_query("SELECT * FROM person_photos WHERE id = %s AND person_id = %s", (photo_id, person_id), fetchone=True)
    if not photo:
        return False, {"message": "Photo record not found.", "error_code": "NOT_FOUND"}, 404

    # Remove physical file if present
    filename = os.path.basename(photo['file_path'])
    upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'assets', 'images', 'uploads', 'person_photos'))
    file_path_full = os.path.join(upload_dir, filename)

    if os.path.exists(file_path_full):
        try:
            os.remove(file_path_full)
        except Exception as e:
            print(f"File delete warning: {e}")

    execute_query("DELETE FROM person_photos WHERE id = %s", (photo_id,), commit=True)

    log_audit_event(
        user_id=current_user['user_id'],
        action="PHOTO_DELETED",
        details={"person_id": person_id, "photo_id": photo_id}
    )

    return True, {"message": "Photo deleted successfully."}, 200

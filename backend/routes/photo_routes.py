from flask import Blueprint, request, jsonify
from utils.auth import token_required
from utils.authorization import verify_person_access
from services.photo_service import save_person_photo, delete_person_photo

photo_bp = Blueprint('photo', __name__, url_prefix='/api/persons')

@photo_bp.route('/<int:person_id>/photos', methods=['POST'])
@token_required
def upload_photo(person_id):
    current_user = getattr(request, 'current_user', {})
    allowed, person, family = verify_person_access(person_id, current_user, required_level='EDITOR')
    if not allowed:
        return jsonify({"success": False, "message": "Forbidden: You are not authorized to upload photos for this person.", "error_code": "FORBIDDEN_PHOTO_UPLOAD"}), 403

    if 'photo' not in request.files:
        return jsonify({"success": False, "message": "No photo file provided in request.", "error_code": "MISSING_FILE"}), 400

    file_obj = request.files['photo']
    success, result, status_code = save_person_photo(person_id, file_obj, current_user)
    if success:
        return jsonify({"success": True, "message": "Photo uploaded successfully.", "data": result}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code')}), status_code

@photo_bp.route('/<int:person_id>/photos/<int:photo_id>', methods=['DELETE'])
@token_required
def delete_photo(person_id, photo_id):
    current_user = getattr(request, 'current_user', {})
    allowed, person, family = verify_person_access(person_id, current_user, required_level='EDITOR')
    if not allowed:
        return jsonify({"success": False, "message": "Forbidden: You are not authorized to delete photos for this person.", "error_code": "FORBIDDEN_PHOTO_DELETE"}), 403

    success, result, status_code = delete_person_photo(person_id, photo_id, current_user)
    if success:
        return jsonify({"success": True, "message": result.get('message'), "data": {}}), status_code
    return jsonify({"success": False, "message": result.get('message'), "error_code": result.get('error_code')}), status_code

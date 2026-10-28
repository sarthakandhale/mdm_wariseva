import os
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from config import Config
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.admin_routes import admin_bp
from routes.audit_routes import audit_bp
from routes.family_routes import family_bp
from routes.person_routes import person_bp
from routes.photo_routes import photo_bp
from routes.emergency_routes import emergency_bp
from routes.medical_routes import medical_bp
from routes.lost_person_routes import lost_person_bp
from routes.found_person_routes import found_person_bp
from routes.item_routes import item_bp
from routes.ai_routes import ai_bp
from routes.dindi_routes import dindi_bp
from routes.route_location_routes import route_loc_bp
from routes.volunteer_routes import vol_bp

frontend_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

app = Flask(__name__, static_folder=frontend_folder, static_url_path='')
app.config.from_object(Config)

# Enable CORS for REST APIs
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Register REST Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(audit_bp)
app.register_blueprint(family_bp)
app.register_blueprint(person_bp)
app.register_blueprint(photo_bp)
app.register_blueprint(emergency_bp)
app.register_blueprint(medical_bp)
app.register_blueprint(lost_person_bp)
app.register_blueprint(found_person_bp)
app.register_blueprint(item_bp)
app.register_blueprint(ai_bp)
app.register_blueprint(dindi_bp)
app.register_blueprint(route_loc_bp)
app.register_blueprint(vol_bp)










# Global Error Handlers for consistent JSON output
@app.errorhandler(400)
def bad_request(e):
    return jsonify({"success": False, "message": "Bad Request", "error_code": "BAD_REQUEST"}), 400

@app.errorhandler(401)
def unauthorized(e):
    return jsonify({"success": False, "message": "Unauthorized access", "error_code": "UNAUTHORIZED"}), 401

@app.errorhandler(403)
def forbidden(e):
    return jsonify({"success": False, "message": "Access forbidden", "error_code": "FORBIDDEN"}), 403

@app.errorhandler(404)
def not_found(e):
    # If path starts with /api/, return JSON 404
    if request.path.startswith('/api/'):
        return jsonify({"success": False, "message": "API endpoint not found", "error_code": "NOT_FOUND"}), 404
    # Otherwise fallback to index.html or static file serving
    return send_from_directory(frontend_folder, 'index.html')

@app.errorhandler(409)
def conflict(e):
    return jsonify({"success": False, "message": "Resource conflict", "error_code": "CONFLICT"}), 409

@app.errorhandler(422)
def unprocessable_entity(e):
    return jsonify({"success": False, "message": "Validation error", "error_code": "VALIDATION_ERROR"}), 422

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"success": False, "message": "Internal server error occurred", "error_code": "SERVER_ERROR"}), 500

# Frontend Static Routing
@app.route('/')
def serve_index():
    return send_from_directory(frontend_folder, 'index.html')

@app.route('/<path:path>')
def serve_frontend_files(path):
    if os.path.exists(os.path.join(frontend_folder, path)):
        return send_from_directory(frontend_folder, path)
    return send_from_directory(frontend_folder, 'index.html')

if __name__ == '__main__':
    print("=" * 65)
    print("  ReuniteAI – AI-Powered Lost Person Platform (Module 1)")
    print("  Case Study: Jagannath Rath Yatra, Puri")
    print("  Running on: http://127.0.0.1:5000")
    print("=" * 65)
    app.run(host='0.0.0.0', port=5000, debug=True)

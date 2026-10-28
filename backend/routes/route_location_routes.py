from flask import Blueprint, request, jsonify
from utils.auth import token_required, role_required
from services.route_location_service import (
    create_wari_route, get_route_details, add_route_section,
    add_wari_location, get_nearby_locations, update_dindi_location,
    get_latest_dindi_location, dindi_checkpoint_checkin,
    update_crowd_zone_status, publish_route_alert
)
from db import execute_query

route_loc_bp = Blueprint('route_locations', __name__, url_prefix='/api')

# --- ROUTES ---
@route_loc_bp.route('/routes', methods=['POST'])
@token_required
@role_required(['EVENT_ADMIN', 'SUPER_ADMIN'])
def create_route_route():
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}
    success, result, status_code = create_wari_route(payload, current_user)
    return jsonify({"success": success, "message": result.get('message', 'Route created.'), "data": result}), status_code

@route_loc_bp.route('/routes', methods=['GET'])
@token_required
def get_routes_route():
    routes = execute_query("SELECT * FROM wari_routes ORDER BY id ASC", fetchall=True) or []
    return jsonify({"success": True, "message": "Routes retrieved.", "data": routes}), 200

@route_loc_bp.route('/routes/<int:route_id>', methods=['GET'])
@token_required
def get_route_by_id_route(route_id):
    route = get_route_details(route_id)
    if not route:
        return jsonify({"success": False, "message": "Route not found."}), 404
    return jsonify({"success": True, "message": "Route details retrieved.", "data": route}), 200

# --- SECTIONS ---
@route_loc_bp.route('/routes/<int:route_id>/sections', methods=['POST'])
@token_required
@role_required(['EVENT_ADMIN', 'SUPER_ADMIN'])
def add_route_section_route(route_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}
    success, result, status_code = add_route_section(route_id, payload, current_user)
    return jsonify({"success": success, "message": result.get('message'), "data": result}), status_code

@route_loc_bp.route('/routes/<int:route_id>/sections', methods=['GET'])
@token_required
def get_route_sections_route(route_id):
    sections = execute_query("SELECT * FROM route_sections WHERE route_id = %s ORDER BY sequence_number ASC", (route_id,), fetchall=True) or []
    return jsonify({"success": True, "message": "Route sections retrieved.", "data": sections}), 200

# --- LOCATIONS & NEARBY SEARCH ---
@route_loc_bp.route('/locations', methods=['POST'])
@token_required
@role_required(['EVENT_ADMIN', 'SUPER_ADMIN', 'HELP_CENTER_OPERATOR', 'POLICE_OFFICER'])
def add_location_route():
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}
    success, result, status_code = add_wari_location(payload, current_user)
    return jsonify({"success": success, "message": result.get('message'), "data": result}), status_code

@route_loc_bp.route('/locations', methods=['GET'])
@token_required
def get_locations_route():
    loc_type = request.args.get('type')
    zone = request.args.get('zone')
    where_clauses = []
    params = []

    if loc_type:
        where_clauses.append("location_type = %s")
        params.append(loc_type)
    if zone:
        where_clauses.append("zone = %s")
        params.append(zone)

    where_str = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    locs = execute_query(f"SELECT * FROM wari_locations {where_str} ORDER BY id ASC", tuple(params), fetchall=True) or []
    return jsonify({"success": True, "message": "Wari locations retrieved.", "data": locs}), 200

@route_loc_bp.route('/locations/nearby', methods=['GET'])
@token_required
def get_nearby_locations_route():
    lat = request.args.get('latitude')
    lon = request.args.get('longitude')
    radius = float(request.args.get('radius', 5.0))
    loc_type = request.args.get('type')

    if not lat or not lon:
        return jsonify({"success": False, "message": "latitude and longitude are required parameters."}), 400

    nearby = get_nearby_locations(float(lat), float(lon), radius_km=radius, loc_type=loc_type)
    return jsonify({"success": True, "message": f"Nearby facilities within {radius} km retrieved.", "data": nearby}), 200

# --- DINDI LOCATION & HISTORY ---
@route_loc_bp.route('/dindis/<int:dindi_id>/location', methods=['POST'])
@token_required
@role_required(['DINDI_LEADER', 'EVENT_ADMIN', 'SUPER_ADMIN'])
def update_dindi_location_route(dindi_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}
    success, result, status_code = update_dindi_location(dindi_id, payload, current_user)
    return jsonify({"success": success, "message": result.get('message'), "data": result}), status_code

@route_loc_bp.route('/dindis/<int:dindi_id>/location', methods=['GET'])
@token_required
def get_dindi_location_route(dindi_id):
    data = get_latest_dindi_location(dindi_id)
    return jsonify({"success": True, "message": "Dindi location data retrieved.", "data": data}), 200

# --- CHECKPOINTS & CHECK-INS ---
@route_loc_bp.route('/checkpoints/<int:checkpoint_id>/checkin', methods=['POST'])
@token_required
@role_required(['DINDI_LEADER', 'EVENT_ADMIN', 'SUPER_ADMIN'])
def checkpoint_checkin_route(checkpoint_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}
    dindi_id = payload.get('dindi_id')
    if not dindi_id:
        return jsonify({"success": False, "message": "dindi_id is required."}), 400

    success, result, status_code = dindi_checkpoint_checkin(dindi_id, checkpoint_id, payload, current_user)
    return jsonify({"success": success, "message": result.get('message'), "data": result}), status_code

# --- CROWD ZONES ---
@route_loc_bp.route('/crowd-zones', methods=['GET'])
@token_required
def get_crowd_zones_route():
    zones = execute_query("SELECT * FROM crowd_zones ORDER BY id ASC", fetchall=True) or []
    return jsonify({"success": True, "message": "Crowd zones retrieved.", "data": zones}), 200

@route_loc_bp.route('/crowd-zones/<int:zone_id>', methods=['PATCH'])
@token_required
@role_required(['POLICE_OFFICER', 'EVENT_ADMIN', 'SUPER_ADMIN'])
def update_crowd_zone_route(zone_id):
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}
    success, result, status_code = update_crowd_zone_status(zone_id, payload, current_user)
    return jsonify({"success": success, "message": result.get('message')}), status_code

# --- ROUTE ALERTS ---
@route_loc_bp.route('/routes/alerts', methods=['POST'])
@token_required
@role_required(['EVENT_ADMIN', 'SUPER_ADMIN', 'POLICE_OFFICER'])
def publish_route_alert_route():
    current_user = getattr(request, 'current_user', {})
    payload = request.get_json() or {}
    success, result, status_code = publish_route_alert(payload, current_user)
    return jsonify({"success": success, "message": result.get('message'), "data": result}), status_code

@route_loc_bp.route('/routes/alerts', methods=['GET'])
@token_required
def get_route_alerts_route():
    alerts = execute_query("SELECT * FROM route_alerts WHERE status = 'ACTIVE' ORDER BY id DESC", fetchall=True) or []
    return jsonify({"success": True, "message": "Route alerts retrieved.", "data": alerts}), 200

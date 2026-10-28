import math
import uuid
from datetime import datetime
from db import execute_query
from services.audit_service import log_audit_event

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """Calculates approximate straight-line distance in kilometers between two GPS coordinates"""
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return None

    R = 6371.0 # Radius of earth in km
    dlat = math.radians(float(lat2) - float(lat1))
    dlon = math.radians(float(lon2) - float(lon1))
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(float(lat1))) * math.cos(math.radians(float(lat2))) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def generate_route_code():
    """Generates unique Wari Route Code: WS-ROUTE-2026-XXXXXX"""
    res = execute_query("SELECT COUNT(*) as cnt FROM wari_routes", fetchone=True)
    next_num = (res['cnt'] if res else 0) + 1
    return f"WS-ROUTE-2026-{next_num:06d}"

def create_wari_route(payload, current_user):
    """Creates a new Wari route definition"""
    user_id = current_user['user_id']
    route_code = generate_route_code()
    route_uuid = f"route-{uuid.uuid4().hex[:12]}"

    name = payload.get('name', 'Alandi–Pandharpur Palkhi Route').strip()
    start_loc = payload.get('start_location', 'Alandi').strip()
    dest = payload.get('destination', 'Pandharpur').strip()
    distance = float(payload.get('total_distance', 242.5))

    route_id = execute_query("""
    INSERT INTO wari_routes (uuid, route_code, name, start_location, destination, total_distance, status)
    VALUES (%s, %s, %s, %s, %s, %s, 'ACTIVE')
    """, (route_uuid, route_code, name, start_loc, dest, distance), commit=True)

    log_audit_event(user_id, "ROUTE_CREATED", {"route_id": route_id, "route_code": route_code})
    return True, get_route_details(route_id), 201

def get_route_details(route_id):
    """Retrieves route details, section breakdown, and total distance progress"""
    route = execute_query("SELECT * FROM wari_routes WHERE id = %s", (route_id,), fetchone=True)
    if not route:
        return None

    sections = execute_query("""
    SELECT * FROM route_sections WHERE route_id = %s ORDER BY sequence_number ASC
    """, (route_id,), fetchall=True) or []

    route['sections'] = sections
    return route

def add_route_section(route_id, payload, current_user):
    """Adds a section to a Wari route"""
    seq = int(payload.get('sequence_number', 1))
    code = f"SEC-{route_id:02d}-{seq:02d}"
    start_loc = payload.get('start_location', 'Alandi').strip()
    end_loc = payload.get('end_location', 'Pune').strip()
    dist = float(payload.get('distance_km', 20.0))
    dur = payload.get('estimated_duration', '1 Day').strip()

    sec_id = execute_query("""
    INSERT INTO route_sections (
        route_id, section_code, sequence_number, start_location, end_location, distance_km, estimated_duration, status
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'ACTIVE')
    """, (route_id, code, seq, start_loc, end_loc, dist, dur), commit=True)

    return True, {"message": "Route section added.", "section_id": sec_id}, 201

def add_wari_location(payload, current_user):
    """Registers a physical facility or location checkpoint along the route"""
    user_id = current_user['user_id']
    loc_uuid = f"loc-{uuid.uuid4().hex[:12]}"

    name = payload.get('name', 'Wari Facility').strip()
    loc_type = payload.get('location_type', 'OTHER')
    sec_id = payload.get('route_section_id')
    zone = payload.get('zone', 'Saswad').strip()
    lat = float(payload.get('latitude', 18.345))
    lon = float(payload.get('longitude', 74.032))
    desc = payload.get('description', '').strip()
    phone = payload.get('contact_number', '').strip()

    loc_id = execute_query("""
    INSERT INTO wari_locations (
        uuid, name, location_type, route_section_id, zone, latitude, longitude, description, contact_number, status
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'OPEN')
    """, (loc_uuid, name, loc_type, sec_id, zone, lat, lon, desc, phone), commit=True)

    log_audit_event(user_id, "LOCATION_CREATED", {"location_id": loc_id, "name": name, "type": loc_type})
    return True, {"message": "Wari location registered.", "location_id": loc_id}, 201

def get_nearby_locations(lat, lon, radius_km=5.0, loc_type=None):
    """
    Finds nearby medical camps, help centers, water points, rest spots using Haversine formula.
    Returns list sorted by distance_km ASC.
    """
    where_clauses = ["status = 'OPEN'"]
    params = []

    if loc_type:
        where_clauses.append("location_type = %s")
        params.append(loc_type)

    where_str = " WHERE " + " AND ".join(where_clauses)
    all_locs = execute_query(f"SELECT * FROM wari_locations {where_str}", tuple(params), fetchall=True) or []

    nearby = []
    for l in all_locs:
        d = calculate_haversine_distance(lat, lon, l['latitude'], l['longitude'])
        if d is not None and d <= float(radius_km):
            l['distance_km'] = d
            nearby.append(l)

    nearby.sort(key=lambda x: x['distance_km'])
    return nearby

def update_dindi_location(dindi_id, payload, current_user):
    """
    Updates current Dindi location (GPS or manual) and appends to history log.
    """
    user_id = current_user['user_id']
    lat = float(payload.get('latitude', 18.345))
    lon = float(payload.get('longitude', 74.032))
    acc = float(payload.get('accuracy', 15.0))
    src = payload.get('location_source', 'MANUAL')
    status = payload.get('status', 'MOVING')

    update_id = execute_query("""
    INSERT INTO dindi_location_updates (dindi_id, latitude, longitude, accuracy, location_source, status, recorded_by)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (dindi_id, lat, lon, acc, src, status, user_id), commit=True)

    log_audit_event(user_id, "DINDI_LOCATION_UPDATED", {"dindi_id": dindi_id, "lat": lat, "lon": lon, "source": src})
    return True, {"message": "Dindi location updated.", "update_id": update_id}, 201

def get_latest_dindi_location(dindi_id):
    """Retrieves latest Dindi location update and recent movement history"""
    latest = execute_query("""
    SELECT u.*, us.full_name as recorder_name
    FROM dindi_location_updates u
    JOIN users us ON u.recorded_by = us.id
    WHERE u.dindi_id = %s
    ORDER BY u.id DESC LIMIT 1
    """, (dindi_id,), fetchone=True)

    history = execute_query("""
    SELECT * FROM dindi_location_updates WHERE dindi_id = %s ORDER BY id DESC LIMIT 10
    """, (dindi_id,), fetchall=True) or []

    checkins = execute_query("""
    SELECT c.*, wl.name as checkpoint_name
    FROM dindi_checkins c
    JOIN wari_locations wl ON c.checkpoint_id = wl.id
    WHERE c.dindi_id = %s ORDER BY c.id DESC
    """, (dindi_id,), fetchall=True) or []

    return {
        "latest_location": latest or {},
        "location_history": history,
        "checkins": checkins
    }

def dindi_checkpoint_checkin(dindi_id, checkpoint_id, payload, current_user):
    """Registers official Dindi passage check-in at a route checkpoint"""
    user_id = current_user['user_id']
    lat = payload.get('latitude')
    lon = payload.get('longitude')
    status = payload.get('status', 'PASSED')

    checkin_id = execute_query("""
    INSERT INTO dindi_checkins (dindi_id, checkpoint_id, checked_in_by, latitude, longitude, status)
    VALUES (%s, %s, %s, %s, %s, %s)
    """, (dindi_id, checkpoint_id, user_id, lat, lon, status), commit=True)

    log_audit_event(user_id, "DINDI_CHECKED_IN", {"dindi_id": dindi_id, "checkpoint_id": checkpoint_id, "status": status})
    return True, {"message": "Dindi checked in successfully at checkpoint.", "checkin_id": checkin_id}, 201

def update_crowd_zone_status(zone_id, payload, current_user):
    """Updates crowd congestion level (`LOW`, `MODERATE`, `HIGH`, `SEVERE`)"""
    user_id = current_user['user_id']
    level = payload.get('crowd_level', 'MODERATE')

    execute_query("""
    UPDATE crowd_zones SET crowd_level = %s, updated_by = %s, last_updated = NOW() WHERE id = %s
    """, (level, user_id, zone_id), commit=True)

    log_audit_event(user_id, "CROWD_STATUS_UPDATED", {"zone_id": zone_id, "crowd_level": level})
    return True, {"message": f"Crowd zone status updated to {level}."}, 200

def publish_route_alert(payload, current_user):
    """Publishes a route alert to pilgrims and operators"""
    user_id = current_user['user_id']
    sec_id = payload.get('route_section_id')
    title = payload.get('title', 'Route Notice').strip()
    msg = payload.get('message', '').strip()
    priority = payload.get('priority', 'NORMAL')

    alert_id = execute_query("""
    INSERT INTO route_alerts (route_section_id, title, message, priority, created_by, status)
    VALUES (%s, %s, %s, %s, %s, 'ACTIVE')
    """, (sec_id, title, msg, priority, user_id), commit=True)

    log_audit_event(user_id, "ROUTE_ALERT_CREATED", {"alert_id": alert_id, "priority": priority})
    return True, {"message": "Route alert published.", "alert_id": alert_id}, 201

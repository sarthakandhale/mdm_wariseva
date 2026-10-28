import math
from db import execute_query
from services.audit_service import log_audit_event

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculates distance in kilometers between two GPS coordinates using Haversine formula.
    """
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 999.0

    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def list_medical_facilities(zone=None, facility_type=None, status=None):
    where_clauses = []
    params = []

    if zone:
        where_clauses.append("f.zone = %s")
        params.append(zone)

    if facility_type:
        where_clauses.append("f.facility_type = %s")
        params.append(facility_type)

    if status:
        where_clauses.append("f.status = %s")
        params.append(status)

    where_str = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    query = f"""
    SELECT f.*, 
           (f.capacity - f.current_patients) as available_capacity,
           CASE 
               WHEN f.current_patients >= f.capacity THEN 'FULL'
               WHEN f.current_patients >= (f.capacity * 0.8) THEN 'BUSY'
               ELSE 'AVAILABLE'
           END as computed_status
    FROM medical_facilities f
    {where_str}
    ORDER BY f.zone ASC, f.name ASC
    """
    facilities = execute_query(query, tuple(params), fetchall=True)

    # Attach services to each facility
    for f in facilities:
        services = execute_query("SELECT service_name FROM medical_facility_services WHERE facility_id = %s AND available = 1", (f['id'],), fetchall=True)
        f['services'] = [s['service_name'] for s in services] if services else []

    return facilities

def get_facility_by_id(facility_id):
    facility = execute_query("SELECT * FROM medical_facilities WHERE id = %s", (facility_id,), fetchone=True)
    if not facility:
        return None

    facility['available_capacity'] = max(0, facility['capacity'] - facility['current_patients'])
    services = execute_query("SELECT service_name FROM medical_facility_services WHERE facility_id = %s AND available = 1", (facility_id,), fetchall=True)
    facility['services'] = [s['service_name'] for s in services] if services else []
    return facility

def find_nearby_facilities(lat, lon, zone=None, limit=5):
    """
    Recommends nearest available medical facilities sorted by distance & capacity.
    """
    facilities = list_medical_facilities(zone=zone)

    for f in facilities:
        dist = calculate_haversine_distance(lat, lon, f['latitude'], f['longitude'])
        f['distance_km'] = dist
        # Simple estimated response time: 3 mins per km
        f['estimated_response_mins'] = max(3, int(dist * 3))

    # Sort by distance
    facilities.sort(key=lambda x: x['distance_km'])
    return facilities[:limit]

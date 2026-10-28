from flask import request
import json
from db import execute_query

def log_audit_event(user_id, action, details=None, ip_address=None, user_agent=None):
    """
    Records an action in the system audit log table.
    """
    if ip_address is None and request:
        ip_address = request.remote_addr
    if user_agent is None and request:
        user_agent = request.headers.get('User-Agent', '')
        
    details_str = json.dumps(details) if isinstance(details, (dict, list)) else (details or '')
    
    query = """
    INSERT INTO audit_logs (user_id, action, details, ip_address, user_agent, created_at)
    VALUES (%s, %s, %s, %s, %s, NOW())
    """
    try:
        execute_query(query, (user_id, action, details_str, ip_address, user_agent), commit=True)
    except Exception as e:
        print(f"Error recording audit log: {e}")

def get_audit_logs(limit=100, offset=0, user_id=None, action=None):
    """
    Retrieves formatted audit logs with optional filters.
    """
    where_clauses = []
    params = []
    
    if user_id:
        where_clauses.append("a.user_id = %s")
        params.append(user_id)
        
    if action:
        where_clauses.append("a.action = %s")
        params.append(action)
        
    where_str = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    
    query = f"""
    SELECT 
        a.id, a.user_id, a.action, a.details, a.ip_address, a.user_agent, a.created_at,
        u.full_name as user_name, u.mobile as user_mobile, r.name as role_name
    FROM audit_logs a
    LEFT JOIN users u ON a.user_id = u.id
    LEFT JOIN roles r ON u.role_id = r.id
    {where_str}
    ORDER BY a.created_at DESC
    LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])
    return execute_query(query, tuple(params), fetchall=True)

from flask import Blueprint, request, jsonify
from services.audit_service import get_audit_logs
from utils.auth import token_required, role_required

audit_bp = Blueprint('audit', __name__, url_prefix='/api/admin')

@audit_bp.route('/audit-logs', methods=['GET'])
@token_required
@role_required(['EVENT_ADMIN', 'SUPER_ADMIN'])
def get_logs():
    user_id = request.args.get('user_id')
    action = request.args.get('action')
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    
    logs = get_audit_logs(limit=limit, offset=offset, user_id=user_id, action=action)
    return jsonify({
        "success": True, 
        "message": "Audit logs retrieved successfully.", 
        "data": {
            "logs": logs,
            "count": len(logs),
            "limit": limit,
            "offset": offset
        }
    }), 200

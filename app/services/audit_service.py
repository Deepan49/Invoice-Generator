from flask import request, current_app
from flask_login import current_user
from app.extensions import db
from app.models.audit_log import AuditLog
import json

def log_action(action, entity=None, entity_id=None, metadata=None):
    """
    Utility to log an action to the audit_logs table.
    """
    try:
        user_id = current_user.id if current_user.is_authenticated else None
        org_id = current_user.organization_id if current_user.is_authenticated else None
        
        log = AuditLog(
            user_id=user_id,
            organization_id=org_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            ip_address=request.remote_addr,
            metadata_json=metadata
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        # Don't break the main flow if logging fails
        current_app.logger.error(f"Audit log failed: {str(e)}")

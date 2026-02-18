from functools import wraps
import hashlib
from flask import flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from app.models.api_key import ApiKey

def admin_required(f):
    @wraps(f)
    @login_required 
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash("You do not have permission to access this page.", "error")
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def require_plan(plan_level):
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            # Check if organization has an active subscription of required level
            subscription = current_user.organization.subscription
            if not subscription or subscription.status != 'active':
                flash(f"This feature requires a {plan_level} plan.", "warning")
                return redirect(url_for('settings.upgrade_page'))
            
            # Simple check, can be expanded to check specific levels (e.g., pro includes basic)
            if subscription.plan.name.lower() != plan_level.lower() and plan_level.lower() != 'basic':
                 flash(f"This feature requires a higher plan.", "warning")
                 return redirect(url_for('settings.upgrade_page'))
                 
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Unauthorized', 'message': 'API key required'}), 401
        
        token = auth_header.split(' ')[1]
        key_hash = hashlib.sha256(token.encode()).hexdigest()
        
        api_key = ApiKey.query.filter_by(key_hash=key_hash, is_active=True).first()
        if not api_key:
            return jsonify({'error': 'Unauthorized', 'message': 'Invalid API key'}), 401
            
        # Optional: update last_used_at
        api_key.last_used_at = datetime.utcnow()
        db.session.commit()
        
        return f(*args, **kwargs)
    return decorated_function

def owner_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        # Allow Owner or Admin (role based)
        if current_user.role not in ['Owner', 'Admin']:
             flash("Restricted access.", "error")
             return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

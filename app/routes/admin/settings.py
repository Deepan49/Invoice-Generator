from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models.system_settings import SystemSettings
from app.utils.admin_permissions import super_admin_required
from app.services.admin_service import AdminService
from app.services.security_service import log_admin_action

bp = Blueprint('admin_settings', __name__, url_prefix='/admin/settings')

@bp.route('/')
@login_required
@super_admin_required
def index():
    settings = SystemSettings.get_settings()
    return render_template('admin/settings.html', settings=settings)

@bp.route('/save', methods=['POST'])
@login_required
@super_admin_required
@log_admin_action("UPDATE_SETTINGS")
def save():
    settings = SystemSettings.get_settings()
    
    settings.platform_name = request.form.get('platform_name')
    settings.email_sender = request.form.get('system_email')
    settings.maintenance_mode = 'maintenance_mode' in request.form
    settings.api_rate_limit = int(request.form.get('api_rate_limit', 60))
    settings.max_upload_size = int(request.form.get('max_upload_size', 5))
    
    db.session.commit()
    # Manual call removed as decorator handles it
    
    flash("Platform settings updated successfully.")
    return redirect(url_for('admin_settings.index'))

from flask import Blueprint, render_template, request
from flask_login import login_required
from app.utils.admin_permissions import super_admin_required
from app.models.admin_log import AdminLog
from app.models.user import User
from datetime import datetime

bp = Blueprint('admin_logs', __name__, url_prefix='/admin/logs')

@bp.route('/')
@login_required
@super_admin_required
def index():
    page = request.args.get('page', 1, type=int)
    admin_id = request.args.get('admin_id', type=int)
    action = request.args.get('action')
    date_str = request.args.get('date')
    
    query = AdminLog.query
    
    if admin_id:
        query = query.filter(AdminLog.admin_id == admin_id)
    if action:
        query = query.filter(AdminLog.action == action)
    if date_str:
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            query = query.filter(AdminLog.timestamp >= date_obj)
        except ValueError:
            pass
            
    pagination = query.order_by(AdminLog.timestamp.desc()).paginate(page=page, per_page=20)
    admins = User.query.filter(User.role.in_(['super_admin', 'admin'])).all()
    
    return render_template('admin/logs.html', pagination=pagination, admins=admins)

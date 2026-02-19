from flask import Blueprint, render_template
from flask_login import login_required
from app.utils.admin_permissions import super_admin_required
from app.services.admin_service import AdminService

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/dashboard')
@login_required
@super_admin_required
def dashboard():
    stats = AdminService.get_platform_stats()
    chart_data = AdminService.get_revenue_chart_data()
    return render_template('admin/dashboard.html', stats=stats, chart_data=chart_data)

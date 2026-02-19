from flask import Blueprint, render_template, request
from flask_login import login_required
from app.utils.admin_permissions import super_admin_required
from app.models import Organization

bp = Blueprint('admin_orgs', __name__, url_prefix='/admin/orgs')

@bp.route('/')
@login_required
@super_admin_required
def index():
    orgs = Organization.query.all()
    return render_template('admin/orgs.html', orgs=orgs)

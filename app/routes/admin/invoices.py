from flask import Blueprint, render_template, request
from flask_login import login_required
from app.utils.admin_permissions import super_admin_required
from app.models import Invoice

bp = Blueprint('admin_invoices', __name__, url_prefix='/admin/invoices')

@bp.route('/')
@login_required
@super_admin_required
def index():
    status = request.args.get('status', '')
    if status:
        invoices = Invoice.query.filter_by(status=status).all()
    else:
        invoices = Invoice.query.all()
    return render_template('admin/invoices.html', invoices=invoices)

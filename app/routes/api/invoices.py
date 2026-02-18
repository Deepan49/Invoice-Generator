from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Invoice
from app.extensions import db
from datetime import datetime

bp = Blueprint('api_invoices', __name__, url_prefix='/invoices')

@bp.route('/', methods=['GET'])
@login_required
def get_invoices():
    invoices = Invoice.query.filter_by(organization_id=current_user.organization_id).all()
    data = [{
        'id': i.id,
        'number': i.invoice_number,
        'amount': i.amount,
        'status': i.status,
        'date': i.issue_date.isoformat(),
        'client': i.client.name
    } for i in invoices]
    return jsonify(data)

@bp.route('/', methods=['POST'])
@login_required
def create_invoice():
    # Simplistic creation for API - in real world would need complex nested data
    return jsonify({'error': 'Not implemented for complex invoice creation via simple API yet'}), 501

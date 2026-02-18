from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Client
from app.extensions import db

bp = Blueprint('api_clients', __name__, url_prefix='/clients')

@bp.route('/', methods=['GET'])
@login_required
def get_clients():
    clients = Client.query.filter_by(organization_id=current_user.organization_id).all()
    data = [{
        'id': c.id,
        'name': c.name,
        'email': c.email,
        'phone': c.phone,
        'status': 'Active' # Placeholder
    } for c in clients]
    return jsonify(data)

@bp.route('/', methods=['POST'])
@login_required
def create_client():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('email'):
        return jsonify({'error': 'Name and email are required'}), 400
        
    new_client = Client(
        name=data['name'],
        email=data['email'],
        phone=data.get('phone'),
        organization_id=current_user.organization_id
    )
    db.session.add(new_client)
    db.session.commit()
    return jsonify({'message': 'Client created', 'id': new_client.id}), 201

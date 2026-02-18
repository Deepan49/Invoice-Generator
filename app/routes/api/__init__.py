from flask import Blueprint
from .invoices import bp as invoices_bp
from .clients import bp as clients_bp
from .dashboard import bp as dashboard_bp

bp = Blueprint('api', __name__, url_prefix='/api')

bp.register_blueprint(invoices_bp)
bp.register_blueprint(clients_bp)
bp.register_blueprint(dashboard_bp)

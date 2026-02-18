from .auth import bp as auth_bp
from .main import bp as main_bp
from .invoices import bp as invoices_bp
from .clients import bp as clients_bp
from .products import bp as products_bp
from .settings import bp as settings_bp
from .admin import bp as admin_bp
from .api import bp as api_bp
from .webhooks import bp as webhooks_bp

def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(invoices_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(webhooks_bp)

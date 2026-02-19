from .auth import bp as auth_bp
from .main import bp as main_bp
from .invoices import bp as invoices_bp
from .clients import bp as clients_bp
from .products import bp as products_bp
from .settings import bp as settings_bp
from .admin.dashboard import bp as admin_dashboard_bp
from .admin.users import bp as admin_users_bp
from .admin.orgs import bp as admin_orgs_bp
from .admin.invoices import bp as admin_invoices_bp
from .admin.subscriptions import bp as admin_subscriptions_bp
from .admin.logs import bp as admin_logs_bp
from .admin.settings import bp as admin_settings_bp
from .api import bp as api_bp
from .webhooks import bp as webhooks_bp

def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(invoices_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(admin_dashboard_bp)
    app.register_blueprint(admin_users_bp)
    app.register_blueprint(admin_orgs_bp)
    app.register_blueprint(admin_invoices_bp)
    app.register_blueprint(admin_subscriptions_bp)
    app.register_blueprint(admin_logs_bp)
    app.register_blueprint(admin_settings_bp)
    
    # Admin Security Blueprints
    from .admin.security_routes import bp as admin_security_bp
    app.register_blueprint(admin_security_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(webhooks_bp)

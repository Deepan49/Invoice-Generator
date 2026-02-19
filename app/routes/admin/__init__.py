from flask import Blueprint
from .dashboard import bp as dashboard_bp
from .users import bp as users_bp
from .orgs import bp as orgs_bp
from .invoices import bp as invoices_bp
from .subscriptions import bp as subscriptions_bp
from .logs import bp as logs_bp
from .settings import bp as settings_bp

# This file can be used to aggregate all admin sub-blueprints if needed,
# or we can just import them in app/routes/__init__.py.
# For simplicity in this structure, we'll let app/routes/__init__.py import the dashboard.py 
# and we'll use dashboard.py as the main entry point for now, 
# but let's actually make it a proper package.

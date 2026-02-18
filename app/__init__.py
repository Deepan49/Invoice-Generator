from flask import Flask
from config import config
from .extensions import db, login_manager, migrate, limiter
from .celery_utils import make_celery
from whitenoise import WhiteNoise

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Static files for production
    app.wsgi_app = WhiteNoise(app.wsgi_app, root='app/static/', prefix='static/')
    
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    
    # Setup Structured Logging
    from .utils.structured_logger import setup_logging
    setup_logging(app)
    
    login_manager.login_view = 'auth.login'
    
    from .routes import register_routes
    register_routes(app)
    
    # Register Health Check
    from .routes.health import bp as health_bp
    app.register_blueprint(health_bp)
    
    # Hook for logging requests or other global enterprise logic
    @app.before_request
    def before_request():
        # Could add structured request logging here
        pass

    from app.utils.helpers import nl2br
    app.jinja_env.filters['nl2br'] = nl2br
    
    return app

def create_celery_app(config_name='default'):
     app = create_app(config_name)
     celery = make_celery(app)
     return celery

from flask import Blueprint, jsonify, current_app
from app.extensions import db
from sqlalchemy import text
import redis

bp = Blueprint('health', __name__, url_prefix='/health')

@bp.route('/')
def health_check():
    status = {'status': 'ok', 'db': 'ok', 'redis': 'ok'}
    status_code = 200
    
    # Check Database
    try:
        db.session.execute(text('SELECT 1'))
    except Exception as e:
        status['db'] = f'error: {str(e)}'
        status['status'] = 'degraded'
        status_code = 503
        
    # Check Redis (Celery)
    try:
        r = redis.from_url(current_app.config['CELERY_BROKER_URL'])
        r.ping()
    except Exception as e:
        status['redis'] = f'error: {str(e)}'
        status['status'] = 'degraded'
        if status_code == 200: 
             status_code = 503
             
    return jsonify(status), status_code

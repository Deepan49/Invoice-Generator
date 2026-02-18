from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address)

@login_manager.user_loader
def load_user(user_id):
    print(f"DEBUG: Loading user ID {user_id}")
    from app.models.user import User
    user = User.query.get(int(user_id))
    print(f"DEBUG: User found? {user is not None}")
    return user

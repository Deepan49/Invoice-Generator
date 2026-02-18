from app import create_app
from app.extensions import db
from app.models.user import User
from werkzeug.security import check_password_hash, generate_password_hash

def check_db():
    app = create_app()
    with app.app_context():
        email = 'deepansenthil098@gmail.com'
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"User {email} NOT found in database!")
            # Let's list all users
            users = User.query.all()
            print(f"Available users: {[u.email for u in users]}")
            return

        print(f"User found: {user.email}")
        password_to_check = '123456789'
        is_match = check_password_hash(user.password, password_to_check)
        print(f"Password match for '{password_to_check}': {is_match}")
        
        if not is_match:
            print("Force updating password...")
            user.password = generate_password_hash(password_to_check)
            db.session.commit()
            print("Password updated successfully.")

if __name__ == '__main__':
    check_db()

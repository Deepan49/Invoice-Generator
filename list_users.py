from app import create_app
from app.models.user import User

def list_users():
    app = create_app()
    with app.app_context():
        users = User.query.all()
        print(f"Total Users: {len(users)}")
        for u in users:
            print(f"- {u.email} (ID: {u.id})")
            
if __name__ == '__main__':
    list_users()

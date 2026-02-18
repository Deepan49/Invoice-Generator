from app import create_app
from app.models.user import User
from app.models.organization import Organization

def inspect():
    app = create_app()
    with app.app_context():
        email = 'deepansenthil098@gmail.com'
        user = User.query.filter_by(email=email).first()
        if user:
            print(f"User: {user.email}")
            print(f"ID: {user.id}")
            print(f"Org ID: {user.organization_id}")
            if user.organization:
                print(f"Org Name: {user.organization.name}")
            else:
                print("Org: MISSING")
        else:
            print("User NOT found")

if __name__ == '__main__':
    inspect()

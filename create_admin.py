from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.organization import Organization, OrganizationSettings
from werkzeug.security import generate_password_hash

def create_admin():
    app = create_app()
    with app.app_context():
        email = 'deepansenthil098@gmail.com'
        username = 'deepan'
        password = '123456789'
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if user:
            print(f"User {email} already exists.")
            return

        # Create Organization
        org = Organization(name="Default Organization")
        db.session.add(org)
        db.session.flush()

        # Create Admin User
        admin = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            is_admin=True,
            role='Owner',
            organization_id=org.id
        )
        db.session.add(admin)
        
        # Create Organization Settings
        settings = OrganizationSettings(organization_id=org.id)
        db.session.add(settings)
        
        db.session.commit()
        print(f"Admin user created successfully!")
        print(f"Email: {email}")
        print(f"Password: {password}")

if __name__ == '__main__':
    create_admin()

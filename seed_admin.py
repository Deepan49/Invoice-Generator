import os
from getpass import getpass
from app import create_app
from app.extensions import db
from app.models.user import User

app = create_app()

with app.app_context():
    email = input("Enter admin email: ").strip().lower()
    username = input("Enter admin username: ").strip()
    password = getpass("Enter admin password: ")
    confirm = getpass("Confirm password: ")

    if password != confirm:
        print("❌ Passwords do not match.")
        exit()

    existing = User.query.filter_by(email=email).first()

    if existing:
        print(f"⚠️ User with email {email} already exists. Updating role to super_admin...")
        existing.role = "super_admin"
        db.session.commit()
        print("✅ User upgraded to Super Admin.")
    else:
        admin = User(
            email=email,
            username=username,
            role="super_admin"
        )
        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()
        print("✅ Super Admin created successfully!")

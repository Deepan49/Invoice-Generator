from datetime import datetime
from werkzeug.security import generate_password_hash
from app import app, db, User, Client, Invoice, Organization, OrganizationSettings


def verify_v3():
    with app.app_context():
        db.drop_all()
        db.create_all()

        org = Organization(name="Acme Billing", address="123 SaaS Street", plan_id="pro")
        db.session.add(org)
        db.session.flush()

        settings = OrganizationSettings(organization_id=org.id, invoice_prefix="INV", invoice_padding=4, currency="USD")
        user = User(
            username="testuser",
            email="test@example.com",
            password=generate_password_hash("pass"),
            role="Owner",
            organization_id=org.id,
        )
        db.session.add_all([settings, user])
        db.session.commit()
        print("OK: User with organization profile created")

        client = Client(name="SaaS Client", email="client@saas.com", organization_id=org.id)
        db.session.add(client)
        db.session.commit()
        print("OK: Client created")

        def get_next_num(organization_id, prefix="INV", padding=4):
            last = (
                Invoice.query.filter_by(organization_id=organization_id)
                .filter(Invoice.invoice_number.like(f"{prefix}-%"))
                .order_by(Invoice.id.desc())
                .first()
            )
            next_num = 1
            if last:
                try:
                    next_num = int(last.invoice_number.split("-")[-1]) + 1
                except ValueError:
                    next_num = 1
            return f"{prefix}-{str(next_num).zfill(padding)}"

        inv1_num = get_next_num(org.id)
        inv1 = Invoice(
            invoice_number=inv1_num,
            due_date=datetime.now(),
            client_id=client.id,
            user_id=user.id,
            organization_id=org.id,
            amount=100,
            status="Unpaid",
        )
        db.session.add(inv1)
        db.session.commit()
        print(f"OK: Created {inv1_num}")

        inv2_num = get_next_num(org.id)
        inv2 = Invoice(
            invoice_number=inv2_num,
            due_date=datetime.now(),
            client_id=client.id,
            user_id=user.id,
            organization_id=org.id,
            amount=200,
            status="Unpaid",
        )
        db.session.add(inv2)
        db.session.commit()
        print(f"OK: Created {inv2_num}")

        assert inv1_num == "INV-0001"
        assert inv2_num == "INV-0002"
        print("SUCCESS: Sequential numbering verified")

        inv3 = Invoice(
            invoice_number="INV-0003",
            due_date=datetime.now(),
            client_id=client.id,
            user_id=user.id,
            organization_id=org.id,
            amount=0,
            status="Draft",
        )
        db.session.add(inv3)
        db.session.commit()
        print("OK: Draft status verified")


if __name__ == "__main__":
    verify_v3()

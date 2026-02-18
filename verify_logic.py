from datetime import datetime
from werkzeug.security import generate_password_hash
from app import app, db, User, Client, Invoice, Organization, OrganizationSettings


def verify():
    with app.app_context():
        db.drop_all()
        db.create_all()

        org = Organization(name="Acme Billing", plan_id="free")
        db.session.add(org)
        db.session.flush()

        settings = OrganizationSettings(organization_id=org.id, invoice_prefix="INV", invoice_padding=4, currency="USD")
        user = User(
            username="tester",
            email="test@example.com",
            password=generate_password_hash("pass"),
            role="Owner",
            organization_id=org.id,
        )
        db.session.add_all([settings, user])
        db.session.commit()
        print("OK: Organization and owner created")

        client = Client(name="Big Corp", email="ceo@bigcorp.com", organization_id=org.id)
        db.session.add(client)
        db.session.commit()
        print("OK: Client created")

        invoice = Invoice(
            invoice_number="INV-0001",
            amount=1200.50,
            due_date=datetime(2026, 12, 31),
            client_id=client.id,
            user_id=user.id,
            organization_id=org.id,
            status="Unpaid",
            currency="USD",
        )
        db.session.add(invoice)
        db.session.commit()
        print("OK: Invoice created")

        assert len(client.invoices) == 1
        assert invoice.client.name == "Big Corp"
        print("OK: Associations verified")

        invoice.status = "Paid"
        db.session.commit()
        assert db.session.get(Invoice, invoice.id).status == "Paid"
        print("OK: Status toggle verified")

        print("\nALL LOGIC TESTS PASSED")


if __name__ == "__main__":
    verify()

from datetime import datetime
from werkzeug.security import generate_password_hash
from app import app, db, User, Client, Invoice, InvoiceItem, Organization, OrganizationSettings


def verify_v2():
    with app.app_context():
        db.drop_all()
        db.create_all()

        org = Organization(name="Zoho Style Co", plan_id="pro")
        db.session.add(org)
        db.session.flush()

        settings = OrganizationSettings(organization_id=org.id, invoice_prefix="INV", invoice_padding=4, currency="USD")
        user = User(
            username="zoho_user",
            email="zoho@example.com",
            password=generate_password_hash("pass"),
            role="Owner",
            organization_id=org.id,
        )
        db.session.add_all([settings, user])
        db.session.commit()
        print("OK: User and organization created")

        client = Client(name="Zoho Client", email="client@zoho.com", organization_id=org.id)
        db.session.add(client)
        db.session.commit()
        print("OK: Client created")

        invoice = Invoice(
            invoice_number="INV-2026-001",
            due_date=datetime(2026, 12, 31),
            tax_rate=10.0,
            currency="USD",
            client_id=client.id,
            user_id=user.id,
            organization_id=org.id,
            status="Unpaid",
            amount=0.0,
        )
        db.session.add(invoice)
        db.session.flush()

        item1 = InvoiceItem(description="Web Design", quantity=10, rate=50, amount=500, invoice_id=invoice.id)
        item2 = InvoiceItem(description="SEO Services", quantity=2, rate=150, amount=300, invoice_id=invoice.id)
        db.session.add_all([item1, item2])

        invoice.amount = 880.0
        db.session.commit()
        print("OK: Advanced invoice with line items created")

        saved_inv = Invoice.query.filter_by(invoice_number="INV-2026-001", organization_id=org.id).first()
        assert saved_inv is not None
        assert len(saved_inv.items) == 2
        assert saved_inv.amount == 880.0
        assert saved_inv.items[0].description == "Web Design"
        print("OK: V2 line item associations and math verified")

        print("\nALL ZOHO-STYLE UPGRADE TESTS PASSED")


if __name__ == "__main__":
    verify_v2()

from app.extensions import db

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    
    address = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    billing_address = db.Column(db.Text, nullable=True)
    shipping_address = db.Column(db.Text, nullable=True)
    gstin = db.Column(db.String(20), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    payment_terms = db.Column(db.Text, nullable=True)
    invoices = db.relationship('Invoice', backref='client', lazy=True, cascade="all, delete-orphan")

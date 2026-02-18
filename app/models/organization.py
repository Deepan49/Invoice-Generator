from datetime import datetime
from app.extensions import db

class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, default="My Company")
    gstin = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    logo_path = db.Column(db.String(150), nullable=True)
    plan_id = db.Column(db.String(20), default='free') # free, pro, enterprise
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    users = db.relationship('User', backref='organization', lazy=True)
    clients = db.relationship('Client', backref='organization', lazy=True)
    products = db.relationship('Product', backref='organization', lazy=True)
    invoices = db.relationship('Invoice', backref='organization', lazy=True)
    settings = db.relationship('OrganizationSettings', backref='organization', uselist=False, lazy=True)

class OrganizationSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    invoice_prefix = db.Column(db.String(20), default="INV")
    invoice_padding = db.Column(db.Integer, default=4)
    currency = db.Column(db.String(10), default="USD")

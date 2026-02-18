from datetime import datetime
from app.extensions import db

class RecurringInvoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Created By
    frequency = db.Column(db.String(20), default='Monthly')
    next_run_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='Active')
    amount = db.Column(db.Numeric(10, 2), default=0.00)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Created By
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    
    invoice_number = db.Column(db.String(50), nullable=False)
    issue_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Draft')
    tax_rate = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), default='USD')
    notes = db.Column(db.Text, nullable=True)
    terms = db.Column(db.Text, nullable=True)
    logo_path = db.Column(db.String(150), nullable=True)
    
    type = db.Column(db.String(20), default='Invoice')
    parent_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=True)
    recurring_id = db.Column(db.Integer, db.ForeignKey('recurring_invoice.id'), nullable=True)
    
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade="all, delete-orphan")

class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=1.0)
    rate = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    discount_type = db.Column(db.String(20), default='None')
    discount_value = db.Column(db.Float, default=0.0)
    tax_rate = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)

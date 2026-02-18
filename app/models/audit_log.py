from datetime import datetime
from app.extensions import db

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False) # e.g., "create_invoice"
    entity = db.Column(db.String(50), nullable=True) # e.g., "invoice"
    entity_id = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True)
    metadata_json = db.Column(db.JSON, nullable=True)
    
    user = db.relationship('User', backref='audit_logs')
    organization = db.relationship('Organization', backref='audit_logs')

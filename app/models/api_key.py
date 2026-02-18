from datetime import datetime
import secrets
import hashlib
from app.extensions import db

class ApiKey(db.Model):
    __tablename__ = 'api_keys'
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    key_hash = db.Column(db.String(128), unique=True, nullable=False)
    key_prefix = db.Column(db.String(8), nullable=False)
    last_used_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    @staticmethod
    def generate_key():
        key = secrets.token_urlsafe(32)
        prefix = key[:8]
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return key, prefix, key_hash

    organization = db.relationship('Organization', backref='api_keys')
    user = db.relationship('User', backref='api_keys')

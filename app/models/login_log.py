from datetime import datetime
from app.extensions import db

class LoginLog(db.Model):
    __tablename__ = 'login_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    device = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    success = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref=db.backref('login_logs', lazy=True))

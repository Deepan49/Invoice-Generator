from app.extensions import db
from datetime import datetime

class SystemSettings(db.Model):
    __tablename__ = 'system_settings'
    id = db.Column(db.Integer, primary_key=True)
    platform_name = db.Column(db.String(100), default='SwiftInvoice')
    email_sender = db.Column(db.String(150), default='noreply@swiftinvoice.com')
    maintenance_mode = db.Column(db.Boolean, default=False)
    api_rate_limit = db.Column(db.Integer, default=60)
    max_upload_size = db.Column(db.Integer, default=5)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get_settings():
        settings = SystemSettings.query.first()
        if not settings:
            settings = SystemSettings()
            db.session.add(settings)
            db.session.commit()
        return settings

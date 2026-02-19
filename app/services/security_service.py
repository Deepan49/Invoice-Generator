import pyotp
import qrcode
import io
import base64
from datetime import datetime, timedelta
from flask import request, current_app, render_template
from flask_mail import Message
from flask_login import current_user
from functools import wraps
from app.extensions import db, mail
from app.models.user import User
from app.models.login_log import LoginLog
from app.models.admin_log import AdminLog
from app.utils.encryption import Encryption
from user_agents import parse

class SecurityService:
    @staticmethod
    def generate_2fa_secret():
        return pyotp.random_base32()

    @staticmethod
    def get_totp_uri(user, secret):
        return pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email,
            issuer_name="SwiftInvoice"
        )

    @staticmethod
    def verify_totp(secret, code):
        totp = pyotp.totp.TOTP(secret)
        return totp.verify(code)

    @staticmethod
    def generate_qr_code(uri):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    @staticmethod
    def log_login(user_id, success=True):
        ua_string = request.headers.get('User-Agent')
        user_agent = parse(ua_string)
        device = f"{user_agent.browser.family} on {user_agent.os.family} ({user_agent.device.family})"
        
        log = LoginLog(
            user_id=user_id,
            ip_address=request.remote_addr,
            device=device,
            location="Unknown", # Integration with GeoIP could go here
            success=success
        )
        db.session.add(log)
        db.session.commit()
        return log

    @staticmethod
    def send_login_alert(user, log):
        msg = Message(
            "New Login Detected - SwiftInvoice",
            recipients=[user.email]
        )
        msg.body = f"""Hi {user.username},
        
New login detected for your account.

Time: {log.timestamp}
IP: {log.ip_address}
Device: {log.device}
Location: {log.location}

If this wasn't you, please change your password immediately and contact support.
"""
        # In a real app, use render_template for HTML emails
        try:
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f"Failed to send login alert: {e}")

def log_admin_action(action_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = f(*args, **kwargs)
            
            # Logic to capture target info from kwargs if possible
            target_id = kwargs.get('user_id') or kwargs.get('org_id') or kwargs.get('invoice_id')
            target_type = None
            if 'user_id' in kwargs: target_type = 'user'
            elif 'org_id' in kwargs: target_type = 'organization'
            elif 'invoice_id' in kwargs: target_type = 'invoice'

            log = AdminLog(
                admin_id=current_user.id,
                action=action_name,
                target_type=target_type,
                target_id=target_id,
                metadata_json={
                    'ip': request.remote_addr,
                    'url': request.url,
                    'method': request.method,
                    'args': request.args.to_dict()
                }
            )
            db.session.add(log)
            db.session.commit()
            return response
        return decorated_function
    return decorator

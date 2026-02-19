from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user, login_user
from app.utils.admin_permissions import super_admin_required
from app.services.security_service import SecurityService
from app.utils.encryption import Encryption
from app.models.user import User
from app.extensions import db, limiter

bp = Blueprint('admin_security', __name__, url_prefix='/admin/security')

@bp.route('/2fa/setup', methods=['GET', 'POST'])
@login_required
@super_admin_required
@limiter.limit("5 per minute")
def setup_2fa():
    if current_user.twofa_enabled:
        flash("2FA is already enabled.")
        return redirect(url_for('admin_settings.index'))

    if request.method == 'POST':
        # Finalize setup
        code = request.form.get('code')
        secret = session.get('temp_2fa_secret')
        if SecurityService.verify_totp(secret, code):
            current_user.twofa_secret = Encryption.encrypt(secret)
            current_user.twofa_enabled = True
            db.session.commit()
            session.pop('temp_2fa_secret', None)
            flash("2FA enabled successfully!")
            return redirect(url_for('admin_settings.index'))
        else:
            flash("Invalid code. Please try again.")

    # Generate new secret for setup
    secret = SecurityService.generate_2fa_secret()
    session['temp_2fa_secret'] = secret
    uri = SecurityService.get_totp_uri(current_user, secret)
    qr_code = SecurityService.generate_qr_code(uri)
    
    return render_template('admin/security/setup_2fa.html', qr_code=qr_code, secret=secret)

@bp.route('/2fa/verify', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def verify_2fa():
    user_id = session.get('2fa_user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    user = User.query.get(user_id)
    if request.method == 'POST':
        code = request.form.get('code')
        secret = Encryption.decrypt(user.twofa_secret)
        if SecurityService.verify_totp(secret, code):
            session.pop('2fa_user_id', None)
            login_user(user)
            log = SecurityService.log_login(user.id, success=True)
            SecurityService.send_login_alert(user, log)
            return redirect(url_for('main.dashboard'))
        else:
            flash("Invalid OTP code.")

    return render_template('admin/security/verify_2fa.html')

@bp.route('/2fa/disable', methods=['POST'])
@login_required
@super_admin_required
def disable_2fa():
    current_user.twofa_enabled = False
    current_user.twofa_secret = None
    db.session.commit()
    flash("2FA has been disabled.")
    return redirect(url_for('admin_settings.index'))

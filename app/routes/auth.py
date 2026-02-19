from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.user import User
from app.extensions import db, limiter
from app.services.security_service import SecurityService
from datetime import datetime, timedelta

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("100 per minute")
def login():
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''

        if not email or not password:
            flash('Email and password are required.')
            return redirect(url_for('auth.login'))

        user = User.query.filter_by(email=email).first()
        
        # Brute-force protection
        if user and user.locked_until and user.locked_until > datetime.utcnow():
            flash(f'Account locked. Try again after {user.locked_until.strftime("%H:%M:%S")}')
            return redirect(url_for('auth.login'))

        if not user or not user.check_password(password):
            if user:
                user.login_attempts += 1
                if user.login_attempts >= 5:
                    user.locked_until = datetime.utcnow() + timedelta(minutes=15)
                    flash('Too many failed attempts. Account locked for 15 minutes.')
                db.session.commit()
                SecurityService.log_login(user.id, success=False)
            flash('Login failed. Check your credentials.')
            return redirect(url_for('auth.login'))
        
        if user.is_suspended:
            flash('Your account has been suspended. Please contact support.')
            return redirect(url_for('auth.login'))
        
        # Reset attempts on success
        user.login_attempts = 0
        user.locked_until = None
        db.session.commit()

        # 2FA Redirection
        if user.role == 'super_admin' and user.twofa_enabled:
            session['2fa_user_id'] = user.id
            return redirect(url_for('admin_security.verify_2fa'))

        login_user(user)
        log = SecurityService.log_login(user.id, success=True)
        SecurityService.send_login_alert(user, log)
        return redirect(url_for('main.dashboard'))
        
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''

        if not username or not email or not password:
            flash('Username, email, and password are required.', 'error')
            return redirect(url_for('auth.signup'))
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists')
            return redirect(url_for('auth.signup'))
        
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            role='Owner',
            is_admin=True
        )
        db.session.add(new_user)
        db.session.flush() 
        
        # Create Organization
        new_org = Organization(name=f"{username}'s Company")
        db.session.add(new_org)
        db.session.flush()
        
        # Link
        new_user.organization_id = new_org.id
        
        # Default Settings
        new_settings = OrganizationSettings(organization_id=new_org.id)
        db.session.add(new_settings)
        
        db.session.commit()
        return redirect(url_for('auth.login'))
        
    return render_template('signup.html')

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import User, Organization, OrganizationSettings
from app.extensions import db, limiter

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
        
        if not user or not check_password_hash(user.password, password):
            flash('Login failed. Check your credentials.')
            return redirect(url_for('auth.login'))
        
        login_user(user)
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

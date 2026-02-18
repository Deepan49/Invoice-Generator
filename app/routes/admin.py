from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from app.models import User, Invoice, Organization
from app.extensions import db
from app.utils.decorators import admin_required, owner_required
import datetime as dt
from werkzeug.security import generate_password_hash

bp = Blueprint('admin', __name__)

# --- Team Management (Org Admin) ---

@bp.route('/team')
@owner_required
def team():
    members = User.query.filter_by(organization_id=current_user.organization_id).all()
    return render_template('team.html', members=members)

@bp.route('/team/add', methods=['POST'])
@owner_required
def add_team_member():
    username = (request.form.get('username') or '').strip()
    email = (request.form.get('email') or '').strip().lower()
    password = request.form.get('password') or ''
    role = request.form.get('role', 'Staff')

    if not username or not email or not password:
        flash('Username, email, and password are required.', 'error')
        return redirect(url_for('admin.team'))
    
    existing = User.query.filter_by(email=email).first()
    if existing:
        flash('User with this email already exists.', 'error')
        return redirect(url_for('admin.team'))
        
    new_user = User(
        username=username, 
        email=email, 
        password=generate_password_hash(password),
        role=role,
        is_admin=(role == 'Admin'),
        organization_id=current_user.organization_id
    )
    db.session.add(new_user)
    db.session.commit()
    flash(f"Team member {username} added successfully.", "success")
    return redirect(url_for('admin.team'))

@bp.route('/team/delete/<int:user_id>', methods=['POST'])
@owner_required
def delete_team_member(user_id):
    user = User.query.get_or_404(user_id)
    if user.organization_id != current_user.organization_id: abort(403)
    if user.id == current_user.id:
        flash("Cannot remove yourself.", "error")
        return redirect(url_for('admin.team'))
        
    db.session.delete(user)
    db.session.commit()
    flash("Team member removed.", "success")
    return redirect(url_for('admin.team'))

# --- Super Admin (Platform Admin) ---

@bp.route('/admin')
@bp.route('/admin/dashboard')
@admin_required
def dashboard():
    total_users = User.query.count()
    total_invoices = Invoice.query.count()
    total_revenue = db.session.query(db.func.sum(Invoice.amount)).scalar() or 0
    recent_users = User.query.order_by(User.id.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                          total_users=total_users, 
                          total_invoices=total_invoices, 
                          total_revenue=total_revenue,
                          recent_users=recent_users)

@bp.route('/admin/users')
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@bp.route('/admin/invoices')
@admin_required
def invoices():
    invoices = Invoice.query.order_by(Invoice.issue_date.desc()).all()
    return render_template('admin/invoices.html', invoices=invoices)

@bp.route('/admin/audit')
@admin_required
def audit_logs():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(200).all()
    return render_template('admin/audit.html', logs=logs)

@bp.route('/admin/api-keys')
@admin_required
def manage_api_keys():
    keys = ApiKey.query.all()
    return render_template('admin/api_keys.html', keys=keys)

@bp.route('/admin/subscriptions')
@admin_required
def subscriptions():
    subs = Subscription.query.all()
    plans = SubscriptionPlan.query.all()
    return render_template('admin/subscriptions.html', subscriptions=subs, plans=plans)

@bp.route('/admin/reports')
@admin_required
def reports():
    total_users = User.query.count()
    total_orgs = Organization.query.count()
    total_invoices = Invoice.query.count()
    total_revenue = db.session.query(db.func.sum(Invoice.amount)).scalar() or 0
    paid_revenue = db.session.query(db.func.sum(Invoice.amount)).filter(Invoice.status == 'Paid').scalar() or 0
    unpaid_revenue = db.session.query(db.func.sum(Invoice.amount)).filter(Invoice.status == 'Unpaid').scalar() or 0

    monthly_rows = (
        db.session.query(
            db.func.strftime('%Y-%m', Invoice.issue_date).label('month'),
            db.func.sum(Invoice.amount).label('amount')
        )
        .group_by('month')
        .order_by('month')
        .all()
    )

    labels = [row.month for row in monthly_rows][-12:]
    values = [float(row.amount or 0) for row in monthly_rows][-12:]

    return render_template(
        'admin/reports.html',
        total_users=total_users,
        total_orgs=total_orgs,
        total_invoices=total_invoices,
        total_revenue=total_revenue,
        paid_revenue=paid_revenue,
        unpaid_revenue=unpaid_revenue,
        report_labels=labels,
        report_values=values
    )

@bp.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot delete yourself!", "error")
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.username} deleted successfully.", "success")
    return redirect(url_for('admin.users'))

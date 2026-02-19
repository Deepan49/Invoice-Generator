from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import User
from app.utils.admin_permissions import super_admin_required
from app.services.admin_service import AdminService
from app.services.security_service import log_admin_action

bp = Blueprint('admin_users', __name__, url_prefix='/admin/users')

@bp.route('/')
@login_required
@super_admin_required
def index():
    query = request.args.get('q', '')
    if query:
        users_list = User.query.filter(User.email.ilike(f'%{query}%') | User.username.ilike(f'%{query}%')).all()
    else:
        users_list = User.query.all()
    return render_template('admin/users.html', users=users_list)

@bp.route('/<int:user_id>/suspend', methods=['POST'])
@login_required
@super_admin_required
@log_admin_action("SUSPEND_USER")
def suspend(user_id):
    if AdminService.suspend_user(current_user.id, user_id):
        flash('User suspended successfully.')
    else:
        flash('User not found.', 'error')
    return redirect(url_for('admin_users.index'))

@bp.route('/<int:user_id>/activate', methods=['POST'])
@login_required
@super_admin_required
@log_admin_action("ACTIVATE_USER")
def activate(user_id):
    if AdminService.activate_user(current_user.id, user_id):
        flash('User activated successfully.')
    else:
        flash('User not found.', 'error')
    return redirect(url_for('admin_users.index'))

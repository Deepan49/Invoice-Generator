from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.subscription import SubscriptionPlan
from app.models.organization import Organization
from app.utils.admin_permissions import super_admin_required
from app.services.admin_service import AdminService
from app.services.security_service import log_admin_action

bp = Blueprint('admin_subscriptions', __name__, url_prefix='/admin/subscriptions')

@bp.route('/')
@login_required
@super_admin_required
def index():
    plans = SubscriptionPlan.query.all()
    # Show all orgs to allow assigning plans to anyone
    orgs = Organization.query.all()
    return render_template('admin/subscriptions.html', plans=plans, all_orgs=orgs)

@bp.route('/assign', methods=['POST'])
@login_required
@super_admin_required
@log_admin_action("CHANGE_PLAN")
def assign_plan():
    org_id = request.form.get('org_id')
    plan_name = request.form.get('plan_name') # 'free', 'pro', 'enterprise'
    
    if AdminService.assign_plan(current_user.id, org_id, plan_name):
        flash(f"Plan updated successfully.")
    else:
        flash("Organization not found.", "error")
    return redirect(url_for('admin_subscriptions.index'))

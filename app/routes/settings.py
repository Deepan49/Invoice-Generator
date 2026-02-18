from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import OrganizationSettings, User
from app.extensions import db

bp = Blueprint('settings', __name__)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        business_name = (request.form.get('business_name') or '').strip()
        if business_name:
            current_user.organization.name = business_name
        current_user.organization.address = request.form.get('business_address')
        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('settings.profile'))
    return render_template('profile.html')

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings_page():
    if not current_user.organization.settings:
         org_settings = OrganizationSettings(organization_id=current_user.organization.id)
         db.session.add(org_settings)
         db.session.commit()
         
    if request.method == 'POST':
        if request.form.get('business_name'):
            current_user.organization.name = request.form.get('business_name')
        if request.form.get('business_address'):
            current_user.organization.address = request.form.get('business_address')
        if request.form.get('gstin'):
            current_user.organization.gstin = request.form.get('gstin')

        current_user.organization.settings.invoice_prefix = request.form.get('invoice_prefix', 'INV').upper()
        try:
            current_user.organization.settings.invoice_padding = int(request.form.get('invoice_padding', 4))
        except ValueError:
            current_user.organization.settings.invoice_padding = 4
        current_user.organization.settings.currency = request.form.get('currency', 'USD')
        
        db.session.commit()
        flash('All settings saved successfully!', 'success')
        return redirect(url_for('settings.settings_page'))
        
    return render_template('settings.html')

@bp.route('/upgrade', methods=['GET'])
@login_required
def upgrade_page():
    return render_template('upgrade.html')

@bp.route('/upgrade/confirm', methods=['POST'])
@login_required
def upgrade_plan():
    plan = request.form.get('plan')
    if plan == 'pro':
        current_user.organization.plan_id = 'pro'
        db.session.commit()
        flash('Upgraded to Pro Plan successfully!', 'success')
    return redirect(url_for('main.dashboard'))

@bp.route('/downgrade', methods=['POST'])
@login_required
def downgrade_plan():
    current_user.organization.plan_id = 'free'
    db.session.commit()
    flash('Downgraded to Free Plan.', 'info')
    return redirect(url_for('main.dashboard'))

@bp.route('/api-key/generate', methods=['POST'])
@login_required
def generate_api_key():
    name = request.form.get('name', 'Default Key')
    key, prefix, key_hash = ApiKey.generate_key()
    
    new_key = ApiKey(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        name=name,
        key_hash=key_hash,
        key_prefix=prefix
    )
    db.session.add(new_key)
    db.session.commit()
    
    flash(f"New API Key generated: {key}. Please copy it now, it won't be shown again.", "success")
    return redirect(url_for('settings.settings_page'))

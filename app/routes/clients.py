from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from app.models import Client
from app.extensions import db

bp = Blueprint('clients', __name__, url_prefix='/clients')

@bp.route('/')
@login_required
def index():
    all_clients = Client.query.filter_by(organization_id=current_user.organization_id).all()
    return render_template('clients.html', clients=all_clients)

@bp.route('/add', methods=['POST'])
@login_required
def add():
    name = (request.form.get('name') or '').strip()
    email = (request.form.get('email') or '').strip().lower()
    phone = request.form.get('phone')
    billing_address = request.form.get('billing_address')
    shipping_address = request.form.get('shipping_address')
    gstin = request.form.get('gstin')
    payment_terms = request.form.get('payment_terms')
    notes = request.form.get('notes')

    if not name or not email:
        flash('Client name and email are required.', 'error')
        return redirect(url_for('clients.index'))
    
    new_client = Client(
        name=name, email=email, phone=phone,
        billing_address=billing_address, shipping_address=shipping_address,
        gstin=gstin, payment_terms=payment_terms, notes=notes,
        organization_id=current_user.organization_id
    )
    db.session.add(new_client)
    db.session.commit()
    flash('Client added successfully!', 'success')
    return redirect(url_for('clients.index'))

@bp.route('/<int:client_id>')
@login_required
def view(client_id):
    client = Client.query.get_or_404(client_id)
    if client.organization_id != current_user.organization_id: abort(403)
    
    total_invoiced = sum(i.amount for i in client.invoices)
    total_paid = sum(i.amount for i in client.invoices if i.status == 'Paid')
    outstanding = sum(i.amount for i in client.invoices if i.status == 'Unpaid')
    
    return render_template('client_view.html', client=client, 
                          total_invoiced=total_invoiced, 
                          total_paid=total_paid, 
                          outstanding=outstanding)

@bp.route('/edit/<int:client_id>', methods=['POST'])
@login_required
def edit(client_id):
    client = Client.query.get_or_404(client_id)
    if client.organization_id != current_user.organization_id: abort(403)
    
    name = (request.form.get('name') or '').strip()
    email = (request.form.get('email') or '').strip().lower()
    if not name or not email:
        flash('Client name and email are required.', 'error')
        return redirect(url_for('clients.view', client_id=client.id))

    client.name = name
    client.email = email
    client.phone = request.form.get('phone')
    client.billing_address = request.form.get('billing_address')
    client.shipping_address = request.form.get('shipping_address')
    client.gstin = request.form.get('gstin')
    client.payment_terms = request.form.get('payment_terms')
    client.notes = request.form.get('notes')
    
    db.session.commit()
    flash('Client updated.', 'success')
    return redirect(url_for('clients.view', client_id=client.id))

@bp.route('/delete/<int:client_id>', methods=['POST'])
@login_required
def delete(client_id):
    client = Client.query.get_or_404(client_id)
    if client.organization_id != current_user.organization_id: abort(403)
    db.session.delete(client)
    db.session.commit()
    flash('Client deleted.', 'success')
    return redirect(url_for('clients.index'))

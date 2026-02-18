from flask import Blueprint, render_template, request, flash, redirect, url_for, abort, send_file, current_app
from flask_login import login_required, current_user
from app.models import Invoice, InvoiceItem, Client, Product, RecurringInvoice, OrganizationSettings
from app.extensions import db
from app.extensions import db, limiter
from app.utils.helpers import parse_float, get_list_value
from app.services.pdf_service import generate_invoice_pdf
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import uuid

bp = Blueprint('invoices', __name__, url_prefix='/invoices')

@bp.route('/')
@login_required
def index():
    status_filter = (request.args.get('status') or 'all').strip()
    query = Invoice.query.filter_by(organization_id=current_user.organization_id)
    if status_filter in {'Paid', 'Unpaid', 'Draft'}:
        query = query.filter_by(status=status_filter)
    invoices = query.order_by(Invoice.issue_date.desc()).all()
    return render_template('invoices.html', invoices=invoices, status_filter=status_filter)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
@limiter.limit("10 per minute")
def create():
    clients = Client.query.filter_by(organization_id=current_user.organization_id).all()
    products = Product.query.filter_by(organization_id=current_user.organization_id).all()
    
    today_date = datetime.now().strftime('%d %b %Y')

    # Auto Invoice Numbering
    org_settings = current_user.organization.settings
    if not org_settings:
        org_settings = OrganizationSettings(organization_id=current_user.organization.id)
        db.session.add(org_settings)
        db.session.commit()
        
    prefix = org_settings.invoice_prefix
    padding = org_settings.invoice_padding
    
    last_invoice = Invoice.query.filter_by(organization_id=current_user.organization_id).filter(Invoice.invoice_number.like(f"{prefix}-%")).order_by(Invoice.id.desc()).first()
    
    new_num = 1
    if last_invoice:
        try:
             last_num = int(last_invoice.invoice_number.split("-")[-1])
             new_num = last_num + 1
        except ValueError:
             new_num = 1
             
    next_invoice_number = f"{prefix}-{str(new_num).zfill(padding)}"
    today_date = datetime.now().strftime('%d %b %Y')

    if request.method == 'POST':
        # --- Check Limits ---
        if current_user.organization.plan_id == 'free':
            cycle_start = datetime.now().replace(day=1, hour=0, minute=0, second=0)
            count = Invoice.query.filter_by(organization_id=current_user.organization_id).filter(Invoice.issue_date >= cycle_start).count()
            
            if count >= 5:
                flash("Free Plan Limit Reached (5 invoices/month). Please upgrade.", "warning")
                return redirect(url_for('settings.upgrade_page')) # Updated ref
        # --------------------

        try:
            client_id_raw = request.form.get('client_id')
            if not client_id_raw:
                raise ValueError("Client is required")
            try:
                client_id = int(client_id_raw)
            except ValueError as exc:
                raise ValueError("Client is invalid") from exc
            client = Client.query.filter_by(id=client_id, organization_id=current_user.organization_id).first()
            if not client:
                raise ValueError("Client is invalid")
                
            due_date_str = request.form.get('due_date')
            if not due_date_str:
                 raise ValueError("Due Date is required")
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            
            tax_rate = 0.0 
            currency = request.form.get('currency', 'USD')
            notes = request.form.get('notes', '')
            terms = request.form.get('terms', '')
            status = request.form.get('status', 'Unpaid')
            inv_type = request.form.get('type', 'Invoice')
            
            # Recurring Logic
            recurring_id = None
            if request.form.get('is_recurring'):
                frequency = request.form.get('recurring_frequency', 'Monthly')
                next_run = due_date
                new_rec = RecurringInvoice(
                    frequency=frequency,
                    next_run_date=next_run,
                    status='Active',
                    amount=0,
                    client_id=client_id,
                    organization_id=current_user.organization_id,
                    user_id=current_user.id
                )
                db.session.add(new_rec)
                db.session.flush()
                recurring_id = new_rec.id

            # Logo
            logo_path = None
            if 'logo' in request.files:
                file = request.files['logo']
                if file and file.filename != '':
                    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                    filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
                    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                    logo_path = os.path.join('uploads', filename)

            new_invoice = Invoice(
                invoice_number=next_invoice_number,
                due_date=due_date, 
                client_id=client_id, 
                organization_id=current_user.organization_id,
                user_id=current_user.id,
                status=status,
                tax_rate=tax_rate,
                currency=currency,
                logo_path=logo_path,
                notes=notes,
                terms=terms,
                type=inv_type,
                recurring_id=recurring_id,
                amount=0.0 
            )
            db.session.add(new_invoice)
            db.session.flush()

            # Process Line Items
            descriptions = request.form.getlist('description[]')
            quantities = request.form.getlist('quantity[]')
            rates = request.form.getlist('rate[]')
            product_ids = request.form.getlist('product_id[]')
            discount_vals = request.form.getlist('discount_value[]')
            discount_types = request.form.getlist('discount_type[]')
            item_taxes = request.form.getlist('item_tax[]')
            
            if not descriptions:
                 raise ValueError("At least one line item is required")
            
            subtotal = 0
            total_tax = 0
            
            for i, desc in enumerate(descriptions):
                if not desc.strip(): continue
                line_no = i + 1
                qty = parse_float(get_list_value(quantities, i, ''), f"Quantity for line {line_no}", default=0.0, minimum=0.0)
                rate = parse_float(get_list_value(rates, i, ''), f"Rate for line {line_no}", default=0.0, minimum=0.0)
                
                disc_val = parse_float(get_list_value(discount_vals, i, ''), f"Discount for line {line_no}", default=0.0, minimum=0.0)
                disc_type = get_list_value(discount_types, i, 'None')
                
                base_amount = qty * rate
                discount_amount = 0
                if disc_type == 'Flat':
                    discount_amount = disc_val
                elif disc_type == 'Percent':
                    discount_amount = base_amount * (disc_val / 100)
                
                amount_after_disc = max(0, base_amount - discount_amount)
                
                i_tax_rate = parse_float(get_list_value(item_taxes, i, ''), f"Tax rate for line {line_no}", default=0.0, minimum=0.0)
                i_tax_amount = amount_after_disc * (i_tax_rate / 100)
                
                item_amount = amount_after_disc
                
                subtotal += item_amount
                total_tax += i_tax_amount
                
                pid_raw = get_list_value(product_ids, i, '')
                pid = None
                if pid_raw:
                    try:
                        pid = int(pid_raw)
                    except ValueError as exc:
                        raise ValueError(f"Product selection is invalid for line {line_no}") from exc

                    product = Product.query.filter_by(id=pid, organization_id=current_user.organization_id).first()
                    if not product:
                        raise ValueError(f"Product selection is invalid for line {line_no}")
                
                new_item = InvoiceItem(
                    description=desc,
                    quantity=qty,
                    rate=rate,
                    amount=item_amount,
                    invoice_id=new_invoice.id,
                    product_id=pid,
                    discount_type=disc_type,
                    discount_value=disc_val,
                    tax_rate=i_tax_rate,
                    tax_amount=i_tax_amount
                )
                db.session.add(new_item)

            if subtotal == 0 and total_tax == 0 and not any((d or '').strip() for d in descriptions):
                raise ValueError("At least one line item is required")
            
            new_invoice.amount = subtotal + total_tax
            new_invoice.tax_rate = 0 
            
            # Update Recurring Amount
            if recurring_id:
                rec_record = db.session.get(RecurringInvoice, recurring_id)
                if rec_record:
                    rec_record.amount = new_invoice.amount
            
            db.session.commit()
            flash(f"{inv_type} {next_invoice_number} created successfully!", "success")
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            print(f"ERROR creating invoice: {e}")
            flash(f"Failed to create invoice: {str(e)}", "error")
            return redirect(url_for('invoices.create'))
        
    return render_template('create_invoice.html', 
                          clients=clients, 
                          products=products,
                          next_invoice_number=next_invoice_number,
                          today_date=today_date)

@bp.route('/status/<int:invoice_id>')
@login_required
def toggle_status(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    if invoice.organization_id != current_user.organization_id:
        abort(403)
    
    invoice.status = 'Paid' if invoice.status == 'Unpaid' else 'Unpaid'
    db.session.commit()
    
    if request.referrer and 'clients' in request.referrer:
        return redirect(request.referrer)
    
    return redirect(url_for('main.dashboard'))

@bp.route('/pdf/<int:invoice_id>')
@login_required
def download_pdf(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    if invoice.organization_id != current_user.organization_id:
        return "Unauthorized", 403
    if not invoice.client:
        return "Invoice client data is missing", 400
    
    buffer = generate_invoice_pdf(invoice, current_user)
    
    return send_file(buffer, as_attachment=True, download_name=f"{invoice.invoice_number}.pdf", mimetype='application/pdf')

@bp.route('/email/<int:invoice_id>')
@login_required
def send_email(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    if invoice.organization_id != current_user.organization_id:
        return "Unauthorized", 403
    if not invoice.client:
        return "Invoice client data is missing", 400
    
    # Simulating email logic
    print(f"SIMULATION: Sending Email to {invoice.client.email}")
    flash(f"Invoice {invoice.invoice_number} sent successfully to {invoice.client.email}!", "success")
    return redirect(url_for('main.dashboard'))

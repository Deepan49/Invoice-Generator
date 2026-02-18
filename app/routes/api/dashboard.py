from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from app.models import Invoice, Client, RecurringInvoice
from datetime import datetime
import datetime as dt

bp = Blueprint('api_dashboard', __name__, url_prefix='/dashboard')

@bp.route('/', methods=['GET'])
@login_required
def get_dashboard_data():
    invoices = Invoice.query.filter_by(organization_id=current_user.organization_id).all()
    clients = Client.query.filter_by(organization_id=current_user.organization_id).all()
    
    total_revenue = sum(inv.amount for inv in invoices if inv.status == 'Paid')
    unpaid_amount = sum(inv.amount for inv in invoices if inv.status == 'Unpaid')
    
    today = datetime.now()
    next_30 = today + dt.timedelta(days=30)
    
    upcoming_invoices = Invoice.query.filter_by(organization_id=current_user.organization_id).filter(Invoice.status=='Unpaid').filter(Invoice.due_date >= today).filter(Invoice.due_date <= next_30).all()
    receivables = sum(i.amount for i in upcoming_invoices)
    
    active_recurring = RecurringInvoice.query.filter_by(organization_id=current_user.organization_id, status='Active').filter(RecurringInvoice.next_run_date <= next_30).all()
    recurring_revenue = sum(r.amount for r in active_recurring)
    
    forecast_amount = receivables + recurring_revenue
    
    return jsonify({
        'total_revenue': total_revenue,
        'unpaid_amount': unpaid_amount,
        'invoice_count': len(invoices),
        'client_count': len(clients),
        'forecast_amount': forecast_amount
    })

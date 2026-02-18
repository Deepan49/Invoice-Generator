from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Invoice, Client, RecurringInvoice
from datetime import datetime
import datetime as dt
import collections

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/pricing')
def pricing():
    return render_template('pricing.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    invoices = Invoice.query.filter_by(organization_id=current_user.organization_id).all()
    clients = Client.query.filter_by(organization_id=current_user.organization_id).all()
    
    total_revenue = sum(inv.amount for inv in invoices if inv.status == 'Paid')
    unpaid_amount = sum(inv.amount for inv in invoices if inv.status == 'Unpaid')
    invoice_count = len(invoices)
    client_count = len(clients)
    
    # Chart Data (Last 6 Months)
    monthly_data = collections.OrderedDict()
    for i in range(5, -1, -1):
        m = (datetime.now().month - i - 1) % 12 + 1
        y = datetime.now().year + (datetime.now().month - i - 1) // 12
        label = datetime(y, m, 1).strftime('%b %Y')
        monthly_data[label] = 0
    
    for inv in invoices:
        if inv.status == 'Paid':
            month_label = inv.issue_date.strftime('%b %Y')
            if month_label in monthly_data:
                monthly_data[month_label] += inv.amount
    
    chart_labels = list(monthly_data.keys())
    chart_values = list(monthly_data.values())
    
    # Forecast
    today = datetime.now()
    next_30 = today + dt.timedelta(days=30)
    
    upcoming_invoices = Invoice.query.filter_by(organization_id=current_user.organization_id).filter(Invoice.status=='Unpaid').filter(Invoice.due_date >= today).filter(Invoice.due_date <= next_30).all()
    receivables = sum(i.amount for i in upcoming_invoices)
    
    active_recurring = RecurringInvoice.query.filter_by(organization_id=current_user.organization_id, status='Active').filter(RecurringInvoice.next_run_date <= next_30).all()
    recurring_revenue = sum(r.amount for r in active_recurring)
    
    forecast_amount = receivables + recurring_revenue
    upcoming_invoices_count = len(upcoming_invoices) + len(active_recurring)
    
    return render_template('dashboard.html', 
                          invoices=invoices, 
                          total_revenue=total_revenue,
                          unpaid_amount=unpaid_amount,
                          invoice_count=invoice_count,
                          client_count=client_count,
                          chart_labels=chart_labels,
                          chart_values=chart_values,
                          forecast_amount=forecast_amount,
                          upcoming_invoices_count=upcoming_invoices_count)

@bp.route('/reports')
@login_required
def reports():
    invoices = (
        Invoice.query
        .filter_by(organization_id=current_user.organization_id)
        .order_by(Invoice.issue_date.desc())
        .all()
    )

    total_invoiced = sum(inv.amount for inv in invoices)
    total_paid = sum(inv.amount for inv in invoices if inv.status == 'Paid')
    total_unpaid = sum(inv.amount for inv in invoices if inv.status == 'Unpaid')
    collection_rate = (total_paid / total_invoiced * 100) if total_invoiced else 0

    monthly = collections.OrderedDict()
    for i in range(5, -1, -1):
        m = (datetime.now().month - i - 1) % 12 + 1
        y = datetime.now().year + (datetime.now().month - i - 1) // 12
        label = datetime(y, m, 1).strftime('%b %Y')
        monthly[label] = 0

    for inv in invoices:
        label = inv.issue_date.strftime('%b %Y')
        if label in monthly:
            monthly[label] += inv.amount

    client_summary = {}
    for inv in invoices:
        client_name = inv.client.name if inv.client else 'Unknown Client'
        if client_name not in client_summary:
            client_summary[client_name] = {'total': 0, 'paid': 0, 'unpaid': 0}
        client_summary[client_name]['total'] += inv.amount
        if inv.status == 'Paid':
            client_summary[client_name]['paid'] += inv.amount
        elif inv.status == 'Unpaid':
            client_summary[client_name]['unpaid'] += inv.amount

    top_clients = sorted(
        [
            {'name': name, **vals}
            for name, vals in client_summary.items()
        ],
        key=lambda x: x['total'],
        reverse=True
    )[:10]

    return render_template(
        'reports.html',
        total_invoiced=total_invoiced,
        total_paid=total_paid,
        total_unpaid=total_unpaid,
        collection_rate=collection_rate,
        report_labels=list(monthly.keys()),
        report_values=list(monthly.values()),
        top_clients=top_clients
    )

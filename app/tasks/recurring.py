import datetime
from app.extensions import db
from app.models import RecurringInvoice, Invoice, InvoiceItem, Organization
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_recurring_invoices(self):
    logger.info("Starting recurring invoice processing task")
    try:
        today = datetime.datetime.now()
        
        # Find active recurring profiles due today or in past
        due_profiles = RecurringInvoice.query.filter(
            RecurringInvoice.status == 'Active',
            RecurringInvoice.next_run_date <= today
        ).all()
        
        logger.info(f"Found {len(due_profiles)} profiles due.")
        
        for profile in due_profiles:
            process_single_profile(profile, today)
            
        db.session.commit()
        logger.info("Recurring invoice processing completed.")
        
    except Exception as exc:
        logger.error(f"Error in recurring task: {exc}")
        db.session.rollback()
        # Retry in 5 minutes
        raise self.retry(exc=exc, countdown=300)

def process_single_profile(profile, today):
    logger.info(f"Processing Profile ID {profile.id}...")
    
    last_invoice = Invoice.query.filter_by(recurring_id=profile.id).order_by(Invoice.id.desc()).first()
    
    if not last_invoice:
        logger.warning(f"Skipping {profile.id}: No parent invoice found.")
        return
        
    # Create New Invoice
    org = Organization.query.get(profile.organization_id)
    if not org:
        logger.warning(f"Skipping {profile.id}: Organization not found.")
        return

    settings = org.settings
    prefix = settings.invoice_prefix if settings else "INV"
    padding = settings.invoice_padding if settings else 4
        
    last_in_org = Invoice.query.filter_by(organization_id=org.id).filter(Invoice.invoice_number.like(f"{prefix}-%")).order_by(Invoice.id.desc()).first()
    new_num = 1
    if last_in_org:
        try: 
            new_num = int(last_in_org.invoice_number.split("-")[-1]) + 1
        except ValueError:
            new_num = 1
    
    new_inv_num = f"{prefix}-{str(new_num).zfill(padding)}"
    
    issue_date = today
    days_gap = (last_invoice.due_date - last_invoice.issue_date).days
    due_date = issue_date + datetime.timedelta(days=days_gap)
    
    new_invoice = Invoice(
        invoice_number=new_inv_num,
        issue_date=issue_date,
        due_date=due_date,
        client_id=profile.client_id,
        organization_id=profile.organization_id,
        user_id=profile.user_id,
        status='Unpaid',
        amount=last_invoice.amount,
        currency=last_invoice.currency,
        notes=last_invoice.notes,
        terms=last_invoice.terms,
        recurring_id=profile.id,
        type='Invoice'
    )
    db.session.add(new_invoice)
    db.session.flush()
    
    for item in last_invoice.items:
        new_item = InvoiceItem(
            invoice_id=new_invoice.id,
            description=item.description,
            quantity=item.quantity,
            rate=item.rate,
            amount=item.amount,
            product_id=item.product_id,
            tax_rate=item.tax_rate,
            tax_amount=item.tax_amount,
            discount_type=item.discount_type,
            discount_value=item.discount_value
        )
        db.session.add(new_item)
    
    next_date = today
    if profile.frequency == 'Daily':
        next_date += datetime.timedelta(days=1)
    elif profile.frequency == 'Weekly':
        next_date += datetime.timedelta(weeks=1)
    elif profile.frequency == 'Monthly':
        next_date += datetime.timedelta(days=30)
    elif profile.frequency == 'Yearly':
        next_date += datetime.timedelta(days=365)
        
    profile.next_run_date = next_date
    logger.info(f"Generated Invoice {new_inv_num} for Profile {profile.id}")

from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Payment, Subscription, SubscriptionPlan, Organization
from app.services.payments import get_payment_provider
import json

bp = Blueprint('webhooks', __name__, url_prefix='/webhooks')

@bp.route('/payment/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    provider = get_payment_provider('stripe')
    event = provider.verify_webhook(payload, sig_header)
    
    if not event:
        return jsonify({'status': 'invalid signature'}), 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_successful_payment(session, 'stripe')
    
    return jsonify({'status': 'success'})

@bp.route('/payment/razorpay', methods=['POST'])
def razorpay_webhook():
    payload = request.get_data()
    sig_header = request.headers.get('X-Razorpay-Signature')
    
    provider = get_payment_provider('razorpay')
    if not provider.verify_webhook(payload, sig_header):
        return jsonify({'status': 'invalid signature'}), 400
        
    data = json.loads(payload)
    if data['event'] == 'payment.captured':
        handle_successful_payment(data['payload']['payment']['entity'], 'razorpay')
        
    return jsonify({'status': 'success'})

def handle_successful_payment(data, provider_name):
    # This is a simplified handler
    # In a real app, you'd extract organization_id from metadata or notes
    metadata = data.get('metadata') or data.get('notes') or {}
    org_id = metadata.get('organization_id')
    plan_name = metadata.get('plan_name')
    
    if not org_id or not plan_name:
        return

    org = Organization.query.get(org_id)
    plan = SubscriptionPlan.query.filter_by(name=plan_name).first()
    
    if org and plan:
        # Create or update subscription
        sub = org.subscription
        if not sub:
            sub = Subscription(organization_id=org.id, plan_id=plan.id)
            db.session.add(sub)
        else:
            sub.plan_id = plan.id
            sub.status = 'active'
        
        # Record payment
        amount = data.get('amount_total') or data.get('amount')
        if provider_name == 'stripe': amount /= 100
        else: amount /= 100
        
        payment = Payment(
            organization_id=org.id,
            amount=amount,
            provider=provider_name,
            status='succeeded',
            transaction_id=data.get('id')
        )
        db.session.add(payment)
        db.session.commit()

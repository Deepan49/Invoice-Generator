import stripe
from flask import current_app
from . import PaymentProvider

class StripeProvider(PaymentProvider):
    def __init__(self):
        stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')

    def create_checkout_session(self, plan_name, amount, currency, organization_id, user_id):
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': currency,
                    'product_data': {'name': plan_name},
                    'unit_amount': int(amount * 100),
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=current_app.config.get('PAYMENT_SUCCESS_URL'),
            cancel_url=current_app.config.get('PAYMENT_CANCEL_URL'),
            metadata={
                'organization_id': organization_id,
                'user_id': user_id,
                'plan_name': plan_name
            }
        )
        return session.url

    def verify_webhook(self, payload, sig_header):
        webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
            return event
        except Exception:
            return None

    def cancel_subscription(self, stripe_subscription_id):
        return stripe.Subscription.delete(stripe_subscription_id)

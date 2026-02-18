import razorpay
from flask import current_app
from . import PaymentProvider

class RazorpayProvider(PaymentProvider):
    def __init__(self):
        self.client = razorpay.Client(auth=(
            current_app.config.get('RAZORPAY_KEY_ID'),
            current_app.config.get('RAZORPAY_KEY_SECRET')
        ))

    def create_checkout_session(self, plan_name, amount, currency, organization_id, user_id):
        # Razorpay uses Orders/Subscriptions differently, this is a simplified version
        order_data = {
            'amount': int(amount * 100),
            'currency': currency,
            'payment_capture': 1,
            'notes': {
                'organization_id': organization_id,
                'user_id': user_id,
                'plan_name': plan_name
            }
        }
        order = self.client.order.create(data=order_data)
        return order['id']

    def verify_webhook(self, payload, sig_header):
        webhook_secret = current_app.config.get('RAZORPAY_WEBHOOK_SECRET')
        try:
            self.client.utility.verify_webhook_signature(payload, sig_header, webhook_secret)
            return True
        except Exception:
            return False

    def cancel_subscription(self, razorpay_subscription_id):
        return self.client.subscription.cancel(razorpay_subscription_id)

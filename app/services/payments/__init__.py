from abc import ABC, abstractmethod

class PaymentProvider(ABC):
    @abstractmethod
    def create_checkout_session(self, plan_name, amount, currency, organization_id, user_id):
        pass

    @abstractmethod
    def verify_webhook(self, payload, sig_header):
        pass

    @abstractmethod
    def cancel_subscription(self, subscription_id):
        pass

def get_payment_provider(provider_name):
    from .stripe_provider import StripeProvider
    from .razorpay_provider import RazorpayProvider
    
    providers = {
        'stripe': StripeProvider,
        'razorpay': RazorpayProvider
    }
    
    provider_class = providers.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Unsupported payment provider: {provider_name}")
        
    return provider_class()

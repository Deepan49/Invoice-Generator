from app import create_app
from app.extensions import db
from app.models.subscription import SubscriptionPlan

def seed_plans():
    app = create_app()
    with app.app_context():
        plans = [
             {'name': 'Free', 'price': 0, 'features': 'Basic Invoicing, 5 Invoices/month'},
             {'name': 'Pro', 'price': 29, 'features': 'Unlimited Invoices, PDF Customization, Recurring Invoices'},
             {'name': 'Enterprise', 'price': 99, 'features': 'Audit Logs, API Access, Dedicated Support'}
        ]
        
        for plan_data in plans:
            plan = SubscriptionPlan.query.filter_by(name=plan_data['name']).first()
            if not plan:
                plan = SubscriptionPlan(
                    name=plan_data['name'],
                    price=plan_data['price'],
                    features=plan_data['features']
                )
                db.session.add(plan)
        
        db.session.commit()
        print("Subscription plans seeded successfully.")

if __name__ == '__main__':
    seed_plans()

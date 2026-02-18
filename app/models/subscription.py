from datetime import datetime
from app.extensions import db

class SubscriptionPlan(db.Model):
    __tablename__ = 'subscription_plans'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    interval = db.Column(db.String(20), default='monthly') # monthly, yearly
    features = db.Column(db.JSON, nullable=True) # {"invoices_per_month": 100, ...}
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=False)
    status = db.Column(db.String(20), default='active') # active, past_due, canceled
    renewal_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    plan = db.relationship('SubscriptionPlan', backref='subscriptions')
    organization = db.relationship('Organization', backref=db.backref('subscription', uselist=False))

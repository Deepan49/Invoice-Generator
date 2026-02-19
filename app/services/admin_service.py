from app.models import User, Organization, Invoice, Subscription
from app.extensions import db
from datetime import datetime, timedelta
from sqlalchemy import func

class AdminService:
    @staticmethod
    def get_platform_stats():
        now = datetime.utcnow()
        last_week = now - timedelta(days=7)
        
        return {
            'total_users': User.query.count(),
            'total_orgs': Organization.query.count(),
            'total_invoices': Invoice.query.count(),
            'new_users_week': User.query.filter(User.created_at >= last_week).count() if hasattr(User, 'created_at') else 0,
            'active_subscriptions': Organization.query.filter(Organization.plan_id != 'free').count(),
            'total_revenue': db.session.query(func.sum(Invoice.amount)).filter(Invoice.status == 'Paid').scalar() or 0
        }

    @staticmethod
    def get_revenue_chart_data():
        # Last 6 months revenue
        now = datetime.utcnow()
        data = []
        for i in range(5, -1, -1):
            month_start = (now.replace(day=1) - timedelta(days=i*30)).replace(day=1, hour=0, minute=0, second=0)
            month_end = (month_start + timedelta(days=32)).replace(day=1)
            
            revenue = db.session.query(func.sum(Invoice.amount))\
                .filter(Invoice.status == 'Paid')\
                .filter(Invoice.issue_date >= month_start)\
                .filter(Invoice.issue_date < month_end).scalar() or 0
            
            data.append({
                'label': month_start.strftime('%b %Y'),
                'value': float(revenue)
            })
        return data

    @staticmethod
    def log_admin_action(admin_id, action, entity, entity_id, metadata=None):
        from app.models.audit_log import AuditLog
        log = AuditLog(
            user_id=admin_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            metadata_json=metadata
        )
        db.session.add(log)
        db.session.commit()

    @staticmethod
    def suspend_user(admin_id, user_id):
        user = User.query.get(user_id)
        if user:
            user.is_suspended = True
            AdminService.log_admin_action(admin_id, 'suspend_user', 'user', user_id)
            db.session.commit()
            return True
        return False

    @staticmethod
    def activate_user(admin_id, user_id):
        user = User.query.get(user_id)
        if user:
            user.is_suspended = False
            AdminService.log_admin_action(admin_id, 'activate_user', 'user', user_id)
            db.session.commit()
            return True
        return False

    @staticmethod
    def assign_plan(admin_id, org_id, plan_name):
        org = Organization.query.get(org_id)
        if org:
            old_plan = org.plan_id
            org.plan_id = plan_name
            AdminService.log_admin_action(admin_id, 'change_plan', 'organization', org_id, {'old_plan': old_plan, 'new_plan': plan_name})
            db.session.commit()
            return True
        return False

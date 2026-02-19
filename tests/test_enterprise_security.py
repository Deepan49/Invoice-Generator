import unittest
import pyotp
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.admin_log import AdminLog
from app.utils.encryption import Encryption
from app.services.security_service import SecurityService

class SecurityTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_2fa_verification(self):
        # Create user with 2FA
        secret = pyotp.random_base32()
        user = User(username='admin', email='admin@test.com', role='super_admin')
        user.set_password('password')
        user.twofa_enabled = True
        user.twofa_secret = Encryption.encrypt(secret)
        db.session.add(user)
        db.session.commit()

        # Generate correct code
        totp = pyotp.totp.TOTP(secret)
        code = totp.now()

        # Verify using service
        self.assertTrue(SecurityService.verify_totp(secret, code))
        
        # Verify with wrong code
        self.assertFalse(SecurityService.verify_totp(secret, '000000'))

    def test_brute_force_lockout(self):
        user = User(username='brute', email='brute@test.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

        # Fail 5 times
        for _ in range(5):
            self.client.post('/login', data={'email': 'brute@test.com', 'password': 'wrong'})
        
        user = User.query.filter_by(email='brute@test.com').first()
        self.assertTrue(user.login_attempts >= 5)
        self.assertIsNotNone(user.locked_until)

    def test_admin_logging_decorator(self):
        # This requires a real request context or manual call
        user = User(username='logger', email='logger@test.com', role='super_admin')
        db.session.add(user)
        db.session.commit()

        # Mock a request inside context
        with self.app.test_request_context('/admin/users/1/suspend', method='POST'):
            from flask_login import login_user
            login_user(user)
            
            from app.services.security_service import log_admin_action
            
            @log_admin_action("TEST_ACTION")
            def dummy_action(user_id=1):
                return "done"
            
            dummy_action(user_id=1)
            
            log = AdminLog.query.filter_by(action='TEST_ACTION').first()
            self.assertIsNotNone(log)
            self.assertEqual(log.admin_id, user.id)
            self.assertEqual(log.target_type, 'user')
            self.assertEqual(log.target_id, 1)

if __name__ == '__main__':
    unittest.main()

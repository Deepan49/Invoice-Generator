import os
from cryptography.fernet import Fernet
from flask import current_app

class Encryption:
    @staticmethod
    def get_fernet():
        key = os.environ.get('FERNET_KEY')
        if not key:
            raise ValueError("FERNET_KEY not found in environment")
        return Fernet(key.encode())

    @classmethod
    def encrypt(cls, data):
        if not data:
            return None
        f = cls.get_fernet()
        return f.encrypt(data.encode()).decode()

    @classmethod
    def decrypt(cls, encrypted_data):
        if not encrypted_data:
            return None
        f = cls.get_fernet()
        return f.decrypt(encrypted_data.encode()).decode()

# Production Setup Guide

## Infrastructure Requirements
- **Database**: PostgreSQL 13+
- **Cache/Broker**: Redis 6+
- **Process Manager**: Systemd or Docker
- **Reverse Proxy**: Nginx with SSL

## Environment Configuration
Create a `.env` file with the following:
```env
FLASK_ENV=production
SECRET_KEY=yoursecret
DATABASE_URL=postgresql://user:pass@localhost/dbname
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Running the Application

### 1. Web Server (Gunicorn)
```bash
gunicorn -c gunicorn.conf.py wsgi:app
```

### 2. Background Worker (Celery)
```bash
celery -A celery_worker.celery worker --loglevel=info
```

### 3. Periodic Tasks (Celery Beat)
```bash
celery -A celery_worker.celery beat --loglevel=info
```

## Security Checklist
- [ ] HTTPS enabled (Nginx)
- [ ] Database backups configured
- [ ] Sentry DSN configured for error tracking
- [ ] Firewall limits access to Redis/Postgres

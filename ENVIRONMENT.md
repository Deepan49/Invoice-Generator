# Environment Variables Guide

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | App environment (`development`, `production`) | `development` |
| `SECRET_KEY` | Secret key for sessions/CSRF | `default-dev-key` |
| `DATABASE_URL` | SQLAlchemy connection string | SQLite |
| `CELERY_BROKER_URL` | Redis URL for Celery broker | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | Redis URL for Celery backend | `redis://localhost:6379/0` |
| `RATELIMIT_STORAGE_URL` | Storage for Rate Limiter | `memory://` |
| `UPLOAD_FOLDER` | Path for file uploads | `app/static/uploads` |
| `SENTRY_DSN` | (Optional) Sentry monitoring URL | - |

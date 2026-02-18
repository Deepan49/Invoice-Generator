# SaaS Invoice Generator

A production-ready Flask application for generating invoices, managing clients, and tracking revenue.

## Features
- Multi-tenancy (Organization-based)
- PDF Invoice Generation
- Recurring Billing Support
- REST API
- Admin Dashboard

## Setup

1. **Clone the repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Environment Setup**:
   Create a `.env` file with:
   ```
   SECRET_KEY=your-secret-key
   DATABASE_URL=sqlite:///database.db
   ```
4. **Run the application**:
   ```bash
   python wsgi.py
   ```
   Or use Flask:
   ```bash
   flask run
   ```

## Development

- **Run Tests**:
  ```bash
  pytest
  ```
- **Database Migrations**:
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

## Architecture

The project follows a modular structure:
- `app/`: Core application package
  - `routes/`: Blueprint definitions
  - `models/`: Database models
  - `services/`: Business logic
  - `tasks/`: Background tasks
- `migrations/`: Database migrations

## API Documentation

- `GET /api/dashboard`: Get dashboard statistics
- `GET /api/clients`: List clients
- `POST /api/clients`: Create a client
- `GET /api/invoices`: List invoices

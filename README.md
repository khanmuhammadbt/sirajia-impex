# Business Management Software

Sirajia Impex is a Flask-based internal billing and ledger application. It helps manage companies, bills, invoice numbers, payments, credit terms, payment status, and printable PDF records.

## Features

- Login-protected billing dashboard
- Create bills with multiple line items
- Add and manage customer companies
- Track pending invoices and payment status
- Record payments and credit-term dates
- Filter billing records by company, bill number, status, month, year, or date
- Generate bill and ledger PDFs
- SQLite database with automatic table creation
- Login rate limiting and temporary account lockout after repeated failures

## Requirements

- Python 3.10 or newer
- A Chromium browser installed by Playwright for PDF generation

Python dependencies are listed in `requirements.txt`.

## Installation

Create and activate a virtual environment from the project directory.

### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
```

If PowerShell blocks script activation for the current terminal, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

## Configuration

Create a `.env` file in the project root. At minimum, set a stable secret key and admin credentials:

```env
SECRET_KEY=replace-with-a-long-random-secret
ADMIN_USERNAME=Admin
ADMIN_PASSWORD_HASH=your-werkzeug-password-hash
```

`ADMIN_PASSWORD_HASH` must be a Werkzeug password hash, not a plain-text password. The first application start creates the admin user when this value is configured.

The default database is SQLite at `instance/data.db` according to Flask's SQLite path handling. The database tables are created automatically when the application starts.

## Run the application

With the virtual environment activated:

```powershell
python app.py
```

Open <http://127.0.0.1:5000> in a browser and sign in with the configured admin account.

## Demo data

The optional seed scripts add sample companies, bills, payments, sellers, and settings:

```powershell
python seed_data.py
python seed_ledger_data.py
```

Run them only when sample data is needed. They are designed to avoid creating duplicate demo records.

## Main routes

| Route | Purpose |
| --- | --- |
| `/login` | Sign in |
| `/dashboard` | Billing dashboard |
| `/bill` | Create a bill |
| `/add_company` | Add or remove companies |
| `/pending` | Review bills without invoice numbers |
| `/credit_terms` | Record payments and credit terms |
| `/record` | View billing and payment records |
| `/generate_pdf` | Download the latest bill as a PDF |
| `/generate_record_pdf` | Download filtered records as a PDF |

## Project structure

```text
app.py                 Flask application entry point
config.py              Environment and application configuration
main/                  Blueprints and route modules
model/                 SQLAlchemy models and data migration helpers
extensions/            Database, rate limiter, and PDF helpers
templates/             Jinja2 templates
static/                CSS, JavaScript, images, and generated PDFs
instance/              Local SQLite database
seed_data.py           General demo data seed
seed_ledger_data.py    Payment ledger demo seed
```

## Security notes

- Never commit `.env`, database files, virtual environments, or generated PDFs.
- Use a strong, unique `SECRET_KEY` in production.
- Use a hashed admin password and do not store plain-text credentials.
- Run the development server with `debug=True` only on a trusted local machine.


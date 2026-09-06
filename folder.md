# Sirajia Impex Folder Structure

```text
sirajia-impex/
|
|-- app.py
|-- config.py
|-- random.html
|-- README.md
|-- requirements.txt
|-- Book1.xlsx
|-- update
|-- folder.md
|
|-- extensions/
|   |-- __init__.py
|   |-- generate_pdf.py
|   `-- __pycache__/                  # Generated Python cache files
|
|-- instance/
|   `-- data.db
|
|-- main/
|   |-- __init__.py
|   |-- routes.py
|   |
|   |-- auth/
|   |   |-- __init__.py
|   |   |-- auth.py
|   |   `-- __pycache__/              # Generated Python cache files
|   |
|   `-- __pycache__/                  # Generated Python cache files
|
|-- model/
|   |-- data.py
|   `-- __pycache__/                  # Generated Python cache files
|
|-- static/
|   |-- css/
|   |   |-- add_company.css
|   |   |-- base.css
|   |   |-- bill.css
|   |   |-- credit_terms.css
|   |   |-- dashboard.css
|   |   |-- login.css
|   |   |-- pending.css
|   |   |-- previous_bills.css
|   |   `-- record.css
|   |
|   |-- img/
|   |   `-- sirajia_impex_logo.png
|   |
|   |-- js/
|   |   `-- bill.js
|   |
|   `-- pdf/
|       |-- bill_pdf.pdf
|       |-- lager_pdf.pdf
|       `-- previous_bill.pdf
|
|-- templates/
|   |-- add_company.html
|   |-- base.html
|   |-- bill.html
|   |-- bill_pdf.html
|   |-- credit _terms.html
|   |-- dashboard.html
|   |-- lager.html
|   |-- login.html
|   |-- pending.html
|   |-- previous_bills.html
|   |-- record.html
|   `-- settings.html
|
|-- __pycache__/                       # Generated Python cache files
|
|-- .git/                              # Git repository metadata
`-- venv/                              # Python virtual environment
```

## Folder Summary

- `main/`: Flask application routes and authentication.
- `model/`: Application data models and database-related code.
- `extensions/`: Flask extensions and PDF generation utilities.
- `templates/`: Jinja2 HTML templates.
- `static/css/`: Stylesheets.
- `static/js/`: Frontend JavaScript files.
- `static/img/`: Images and branding assets.
- `static/pdf/`: Generated PDF files.
- `instance/`: Local application data, including the SQLite database.
- `venv/`: Local Python virtual environment.
- `__pycache__/`: Automatically generated Python bytecode cache files.

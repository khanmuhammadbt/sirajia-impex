from __future__ import annotations

from datetime import datetime

from sqlalchemy import inspect, text

from extensions import db
from .bill import Bill, BillItem, Seller, data
from .company import Company, company_data
from .payment import Payment, payment_data
from .setting import Setting, setting

__all__ = [
    'Company', 'company_data',
    'Seller', 'Bill', 'BillItem', 'data',
    'Payment', 'payment_data',
    'Setting', 'setting',
    'migrate_legacy_database',
]


def _rename_legacy_tables():
    inspector = inspect(db.engine)
    tables = set(inspector.get_table_names())
    renames = {
        'seller': 'legacy_seller',
        'bill': 'legacy_bill',
        'bill_item': 'legacy_bill_item',
        'company_data': 'legacy_company_data',
        'data': 'legacy_data',
        'payment_data': 'legacy_payment_data',
        'setting': 'legacy_setting',
    }
    for old_name, new_name in renames.items():
        if old_name in tables and new_name not in tables:
            db.session.execute(text(f'ALTER TABLE "{old_name}" RENAME TO "{new_name}"'))
    db.session.commit()


def _has_column(table_name, column_name):
    inspector = inspect(db.engine)
    if not inspector.has_table(table_name):
        return False
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def _add_column(table_name, column_name, column_definition):
    if not inspect(db.engine).has_table(table_name):
        return
    if not _has_column(table_name, column_name):
        db.session.execute(text(
            f'ALTER TABLE "{table_name}" ADD COLUMN "{column_name}" {column_definition}'
        ))


def _drop_legacy_indexes():
    inspector = inspect(db.engine)
    for table_name in [
        'legacy_seller', 'legacy_bill', 'legacy_bill_item',
        'legacy_company_data', 'legacy_data', 'legacy_payment_data',
        'legacy_setting',
    ]:
        if not inspector.has_table(table_name):
            continue
        for index in inspector.get_indexes(table_name):
            db.session.execute(text(f'DROP INDEX "{index["name"]}"'))
    db.session.commit()


def migrate_legacy_database():
    inspector = inspect(db.engine)
    tables = set(inspector.get_table_names())

    for old_name in ['seller', 'bill', 'bill_item', 'company_data', 'data', 'payment_data', 'setting']:
        legacy_name = f'legacy_{old_name}'
        if old_name in tables and legacy_name not in tables:
            db.session.execute(text(f'ALTER TABLE "{old_name}" RENAME TO "{legacy_name}"'))
    db.session.commit()

    _add_column('bill', 'created_at', 'DATETIME')
    _add_column('payment', 'created_at', 'DATETIME')
    _add_column('payment', 'bill_id', 'INTEGER')
    _add_column('user', 'failed_login_attempts', 'INTEGER NOT NULL DEFAULT 0')
    _add_column('user', 'locked_until', 'DATETIME')
    db.session.commit()

    if not any(name in tables for name in ['company_data', 'data', 'payment_data', 'setting', 'seller', 'bill', 'bill_item']):
        return

    _drop_legacy_indexes()
    db.create_all()

    if Company.query.first():
        return

    if 'legacy_company_data' in inspect(db.engine).get_table_names():
        rows = db.session.execute(text('SELECT id, company_name, address, ntn, gst, payment_days FROM "legacy_company_data"')).mappings().all()
        for row in rows:
            company = Company(
                name=row['company_name'],
                address=row.get('address'),
                ntn=row.get('ntn'),
                gst=row.get('gst'),
                payment_days=int(row['payment_days']) if row.get('payment_days') is not None else 0,
            )
            db.session.add(company)
        db.session.commit()

    if 'legacy_data' in inspect(db.engine).get_table_names():
        rows = db.session.execute(text('SELECT * FROM "legacy_data" ORDER BY id')).mappings().all()
        for row in rows:
            company_name = (row.get('company_name') or '').strip()
            company = Company.query.filter_by(name=company_name).first()
            if company is None:
                company = Company(name=company_name)
                db.session.add(company)
                db.session.flush()

            bill_date = row.get('date')
            if isinstance(bill_date, str):
                try:
                    bill_date = datetime.strptime(bill_date, '%d-%m-%Y').date()
                except ValueError:
                    try:
                        bill_date = datetime.strptime(bill_date, '%Y-%m-%d').date()
                    except ValueError:
                        bill_date = datetime.utcnow().date()

            bill = Bill.query.filter_by(company_id=company.id, bill_no=row['bill_no']).first()
            if bill is None:
                bill = Bill(
                    company_id=company.id,
                    bill_no=row['bill_no'],
                    date=bill_date,
                    po=row.get('po'),
                    dc=row.get('dc'),
                    order_no=row.get('order_no'),
                    invoice_no=row.get('invoice_no'),
                    tax=row.get('tax'),
                    payment_status=row.get('payment_status') or 'unpaid',
                    paid_amount=row.get('paid_amount') or 0.0,
                    sales_tax=row.get('sales_tax'),
                    grand_total=row.get('grand_total'),
                    final_total=row.get('final_total'),
                    check_no=row.get('check_no'),
                    gate_pass_no=row.get('gate_pass_no'),
                    payment=row.get('payment'),
                )
                if row.get('clear_date'):
                    try:
                        bill.clear_date = datetime.strptime(str(row['clear_date']), '%d-%m-%Y').date()
                    except ValueError:
                        try:
                            bill.clear_date = datetime.strptime(str(row['clear_date']), '%Y-%m-%d').date()
                        except ValueError:
                            pass
                db.session.add(bill)
                db.session.flush()

            item = BillItem(
                bill_id=bill.id,
                description=row.get('description') or '',
                quantity=float(row['quantity']) if row.get('quantity') is not None else 0,
                rate=float(row['rate']) if row.get('rate') is not None else 0.0,
                amount=float(row['amount']) if row.get('amount') is not None else 0.0,
            )
            db.session.add(item)
        db.session.commit()

    if 'legacy_payment_data' in inspect(db.engine).get_table_names():
        rows = db.session.execute(text('SELECT id, company_name, check_no, given_date, clear_date, payment FROM "legacy_payment_data"')).mappings().all()
        for row in rows:
            company = Company.query.filter_by(name=row['company_name']).first()
            if company is None:
                company = Company(name=row['company_name'])
                db.session.add(company)
                db.session.flush()
            payment = Payment(
                company_id=company.id,
                check_no=row['check_no'],
                payment=float(row['payment']) if row.get('payment') is not None else 0.0,
            )
            given = row.get('given_date')
            if isinstance(given, str):
                try:
                    payment.given_date = datetime.strptime(given, '%d-%m-%Y').date()
                except ValueError:
                    try:
                        payment.given_date = datetime.strptime(given, '%Y-%m-%d').date()
                    except ValueError:
                        payment.given_date = datetime.utcnow().date()
            clear = row.get('clear_date')
            if isinstance(clear, str):
                try:
                    payment.clear_date = datetime.strptime(clear, '%d-%m-%Y').date()
                except ValueError:
                    try:
                        payment.clear_date = datetime.strptime(clear, '%Y-%m-%d').date()
                    except ValueError:
                        pass
            db.session.add(payment)
        db.session.commit()

    if 'legacy_setting' in inspect(db.engine).get_table_names():
        row = db.session.execute(text('SELECT id, sales_tax FROM "legacy_setting" ORDER BY id LIMIT 1')).first()
        if row and not Setting.query.first():
            db.session.add(Setting(sales_tax=row[1]))
            db.session.commit()
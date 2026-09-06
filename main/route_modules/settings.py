from flask import flash, redirect, render_template, request, send_file, session, url_for
from extensions import db
from extensions.generate_pdf import generate_pdf as make_pdf
from model.data import company_data, data, payment_data, setting
from model.user import User
from werkzeug.security import check_password_hash, generate_password_hash
from .. import main_bp

@main_bp.route('/settings')
def settings():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    settings = setting.query.first()
    return render_template('settings.html', setting=setting)

@main_bp.route('/setting_sales_tax', methods=['POST'])
def setting_sales_tax():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    sales_tax = request.form.get('sales_tax')
    existing_setting = setting.query.first()
    if existing_setting:
        existing_setting.sales_tax = sales_tax
        db.session.add(existing_setting)
    else:
        db.session.add(setting(sales_tax=sales_tax))
    db.session.commit()
    flash('Settings updated successfully!', 'success')
    return redirect(url_for('main.settings'))

@main_bp.route('/change_password', methods=['POST'])
def change_password():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    user = User.query.filter_by(username=session['username']).first()

    if (not user or not check_password_hash(user.password_hash, current_password)
            or len(new_password) < 8 or new_password != confirm_password):
        flash('Password update failed.', 'error')
        return redirect(url_for('main.settings'))

    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    flash('Password updated successfully.', 'success')
    return redirect(url_for('main.settings'))

@main_bp.route('/lager')
def lager():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    companies = company_data.query.all()
    bills = data.query.all()
    payments = payment_data.query.all()
    ledger_entries = [{'kind': 'bill', 'date': bill.date, 'created_at': bill.created_at, 'id': bill.id, 'item': bill} for bill in bills] + [{'kind': 'payment', 'date': payment.clear_date or payment.given_date, 'created_at': payment.created_at, 'id': payment.id, 'item': payment} for payment in payments]
    ledger_entries.sort(key=lambda entry: (entry['created_at'] is None, entry['created_at'] or entry['date'], entry['id']))
    return render_template('lager.html', ledger_entries=ledger_entries, companies=companies)

@main_bp.route('/generate_lager_pdf')
def generate_lager_pdf():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    company_filter = request.args.get('company', 'all')
    bills = data.query.all()
    payments = payment_data.query.all()
    ledger_entries = [{'kind': 'bill', 'date': bill.date, 'created_at': bill.created_at, 'id': bill.id, 'item': bill} for bill in bills] + [{'kind': 'payment', 'date': payment.clear_date or payment.given_date, 'created_at': payment.created_at, 'id': payment.id, 'item': payment} for payment in payments]
    ledger_entries.sort(key=lambda entry: (entry['created_at'] is None, entry['created_at'] or entry['date'], entry['id']))
    balance = 0
    for entry in ledger_entries:
        if entry['kind'] == 'bill':
            balance += float(entry['item'].final_total or 0)
            balance += float(entry['item'].tax or 0)
        else:
            balance -= float(entry['item'].payment or 0)
        entry['balance'] = balance
    if company_filter != 'all':
        ledger_entries = [entry for entry in ledger_entries if (entry['item'].company_name if entry['kind'] == 'bill' else entry['item'].company.name) == company_filter]
    rendered = render_template('lager_pdf.html', ledger_entries=ledger_entries)
    pdf_file = 'static/pdf/lager_pdf.pdf'
    make_pdf(rendered, pdf_file, 'A4')
    return send_file(pdf_file, as_attachment=True)
import base64
import os
from flask import current_app, redirect, render_template, request, send_file, session, url_for
from extensions import db
from extensions.generate_pdf import generate_pdf as make_pdf
from model.data import company_data, data, payment_data
from .. import main_bp

@main_bp.route('/record')
def record():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    companies = company_data.query.all()
    records = data.query.all()
    payments_by_bill = {}
    for payment in payment_data.query.filter(payment_data.bill_id.isnot(None)).all():
        payments_by_bill.setdefault(payment.bill_id, []).append(payment)
    return render_template('record.html', companies=companies, record=records, payments_by_bill=payments_by_bill)

@main_bp.route('/generate_record_pdf')
def generate_record_pdf():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    company_filter = request.args.get('company', 'all').lower()
    bill_filter = request.args.get('bill', '').lower()
    status_filter = request.args.get('status', 'all').lower()
    month_filter = request.args.get('month', 'all')
    year_filter = request.args.get('year', 'all')
    date_filter = request.args.get('date', '')
    records = []
    for bill in data.query.all():
        bill_date = bill.date.strftime('%Y-%m-%d') if bill.date else ''
        if company_filter != 'all' and (bill.company_name or '').lower() != company_filter:
            continue
        if bill_filter not in str(bill.bill_no).lower():
            continue
        if status_filter != 'all' and (bill.payment_status or 'unpaid').lower() != status_filter:
            continue
        if month_filter != 'all' and not bill_date.startswith(f'{year_filter if year_filter != "all" else bill_date[:4]}-{month_filter}'):
            continue
        if year_filter != 'all' and not bill_date.startswith(f'{year_filter}-'):
            continue
        if date_filter and bill_date != date_filter:
            continue
        for item in bill.items:
            records.append((bill, item))
    payments_by_bill = {}
    for payment in payment_data.query.filter(payment_data.bill_id.isnot(None)).all():
        payments_by_bill.setdefault(payment.bill_id, []).append(payment)
    image_base64 = ''
    image_path = os.path.join(current_app.root_path, 'static', 'img', 'sirajia_impex_logo.png')
    if os.path.exists(image_path):
        with open(image_path, 'rb') as img_file:
            image_base64 = base64.b64encode(img_file.read()).decode('utf-8')
    rendered = render_template('record_pdf.html', records=records, payments_by_bill=payments_by_bill, logo_data=image_base64)
    make_pdf(rendered, 'static/pdf/record_pdf.pdf', 'A4')
    return send_file('static/pdf/record_pdf.pdf', as_attachment=True)
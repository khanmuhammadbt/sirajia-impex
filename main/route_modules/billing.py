from datetime import date as dt_date
import base64
import os
from flask import current_app, flash, redirect, render_template, request, send_file, session, url_for
from extensions import db
from extensions.generate_pdf import generate_pdf as make_pdf
from model.data import Bill, BillItem, company_data, setting
from .. import main_bp

@main_bp.route('/bill')
def bill():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    companies = company_data.query.all()
    settings = db.session.query(setting).first()
    return render_template('bill.html', companies=companies, setting=settings)

@main_bp.route('/add_company')
def add_company():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    return render_template('add_company.html')

@main_bp.route('/add_company_method', methods=['POST'])
def add_comp_method():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    new_company = company_data(company_name=request.form.get('company_name'), address=request.form.get('address'), ntn=request.form.get('ntn'), gst=request.form.get('gst'), payment_days=request.form.get('payment_days'))
    db.session.add(new_company)
    db.session.commit()
    flash('Company details added successfully!', 'success')
    return redirect(url_for('main.add_company'))

@main_bp.route('/delete_company_method', methods=['POST'])
def delete_company_method():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    company_to_delete = company_data.query.filter_by(company_name=request.form.get('company_name')).first()
    if company_to_delete:
        db.session.delete(company_to_delete)
        db.session.commit()
    return redirect(url_for('main.add_company'))

@main_bp.route('/send_data', methods=['POST'])
def send_data():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    descriptions = request.form.getlist('description[]')
    quantities = request.form.getlist('quantity[]')
    rates = request.form.getlist('rate[]')
    company = company_data.query.filter_by(company_name=request.form.get('company_name')).first()
    if company is None:
        company = company_data(company_name=request.form.get('company_name'))
        db.session.add(company)
        db.session.flush()
    try:
        bill_date = dt_date.fromisoformat(request.form.get('date'))
    except Exception:
        bill_date = dt_date.today()
    last_bill = db.session.query(Bill).order_by(Bill.bill_no.desc()).first()
    bill = Bill(company_id=company.id, bill_no=1 if last_bill is None else last_bill.bill_no + 1, date=bill_date, po=request.form.get('po'), dc=request.form.get('dc'), order_no=request.form.get('order_no'), tax=float(request.form.get('sales_tax')) if request.form.get('sales_tax') not in (None, '') else 0.0, sales_tax=setting.query.first().sales_tax if setting.query.first() else 0.0, grand_total=float(request.form.get('grand_total')) if request.form.get('grand_total') not in (None, '') else 0.0, final_total=float(request.form.get('final_total')) if request.form.get('final_total') not in (None, '') else 0.0, gate_pass_no=request.form.get('gate_pass_no'), payment_status='unpaid')
    db.session.add(bill)
    db.session.flush()
    for description, quantity, rate in zip(descriptions, quantities, rates):
        if not description or not quantity or not rate:
            continue
        db.session.add(BillItem(bill_id=bill.id, description=description, quantity=float(quantity), rate=float(rate), amount=float(quantity) * float(rate)))
    db.session.commit()
    flash('Bill saved successfully!', 'success')
    return redirect(url_for('main.bill'))

def _bill_pdf_response(bill, include_logo):
    items = BillItem.query.join(Bill).filter(Bill.bill_no == bill.bill_no).order_by(BillItem.id.asc()).all()
    if not items:
        flash('No items found for the latest bill.', 'error')
        return redirect(url_for('main.bill'))
    values = {'bill_items': items, 'company': bill.company, 'bill_no': bill.bill_no, 'setting': db.session.query(setting).first()}
    if include_logo:
        image_path = os.path.join(current_app.root_path, 'static', 'img', 'sirajia_impex_logo.png')
        image_base64 = ''
        if os.path.exists(image_path):
            with open(image_path, 'rb') as img_file:
                image_base64 = base64.b64encode(img_file.read()).decode('utf-8')
        values['logo_data'] = image_base64
    return render_template('bill_pdf.html', **values)

@main_bp.route('/generate_pdf')
def generate_pdf():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    last_bill = db.session.query(Bill).order_by(Bill.bill_no.desc()).first()
    if not last_bill:
        flash('No bills found to generate PDF.', 'error')
        return redirect(url_for('main.bill'))
    rendered = _bill_pdf_response(last_bill, True)
    if not isinstance(rendered, str):
        return rendered
    pdf_file = 'static/pdf/bill_pdf.pdf'
    make_pdf(rendered, pdf_file, 'A5')
    return send_file(pdf_file, as_attachment=True)

@main_bp.route('/print_bill')
def print_bill():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    last_bill = db.session.query(Bill).order_by(Bill.bill_no.desc()).first()
    if not last_bill:
        flash('No bills found to generate PDF.', 'error')
        return redirect(url_for('main.bill'))
    return _bill_pdf_response(last_bill, False)
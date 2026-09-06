import base64
import os
from flask import current_app, flash, redirect, render_template, request, send_file, session, url_for
from extensions import db
from extensions.generate_pdf import generate_pdf as make_pdf
from model.data import Bill, BillItem, setting
from .. import main_bp

@main_bp.route('/previous_bills')
def previous_bills():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    return render_template('previous_bills.html')

def _find_previous_bill():
    bill_no = request.form.get('bill_no')
    if not bill_no:
        flash('Bill number is required.', 'error')
        return None
    bill = Bill.query.filter_by(bill_no=bill_no).first()
    if bill is None:
        flash('No items found for the specified bill number.', 'error')
        return None
    items = BillItem.query.filter_by(bill_id=bill.id).all()
    if not items:
        flash('No items found for the specified bill number.', 'error')
        return None
    return bill, items

@main_bp.route('/generate_previous_bill_pdf', methods=['POST'])
def generate_previous_bill_pdf():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    found = _find_previous_bill()
    if found is None:
        return redirect(url_for('main.previous_bills'))
    bill, bill_items = found
    image_base64 = ''
    image_path = os.path.join(current_app.root_path, 'static', 'img', 'sirajia_impex_logo.png')
    if os.path.exists(image_path):
        with open(image_path, 'rb') as img_file:
            image_base64 = base64.b64encode(img_file.read()).decode('utf-8')
    rendered = render_template('bill_pdf.html', bill_items=bill_items, company=bill.company, bill_no=bill.bill_no, logo_data=image_base64, setting=db.session.query(setting).first())
    pdf_dir = os.path.join(current_app.root_path, 'static', 'pdf')
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_file = os.path.join(pdf_dir, 'previous_bill.pdf')
    make_pdf(rendered, pdf_file, 'A5')
    return send_file(pdf_file, as_attachment=True)

@main_bp.route('/print_previous_bill', methods=['POST'])
def print_previous_bill():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    found = _find_previous_bill()
    if found is None:
        return redirect(url_for('main.previous_bills'))
    bill, bill_items = found
    return render_template('bill_pdf.html', bill_items=bill_items, company=bill.company, bill_no=bill.bill_no, setting=db.session.query(setting).first())

@main_bp.route('/delete_previous_bill', methods=['POST'])
def delete_previous_bill():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    bill_no = request.form.get('bill_no')
    if not bill_no:
        flash('Bill number is required.', 'error')
        return redirect(url_for('main.previous_bills'))
    bill = Bill.query.filter_by(bill_no=bill_no).first()
    if bill is None:
        flash('No items found for the specified bill number.', 'error')
        return redirect(url_for('main.previous_bills'))
    for item in list(bill.items):
        db.session.delete(item)
    db.session.delete(bill)
    db.session.commit()
    flash('Bill deleted successfully.', 'success')
    return redirect(url_for('main.previous_bills'))
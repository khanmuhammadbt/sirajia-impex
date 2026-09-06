from flask import redirect, render_template, request, url_for, flash, session
from extensions import db
from model.data import data, Bill
from .. import main_bp

@main_bp.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    return redirect(url_for('main.dashboard'))

@main_bp.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    invoice = db.session.query(data).filter(data.invoice_no == None).first()
    return render_template('dashboard.html', invoice=invoice)

@main_bp.route('/pending')
def pending():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    bills = db.session.query(data).filter(data.invoice_no.is_(None)).group_by(data.bill_no).all()
    return render_template('pending.html', bills=bills)

@main_bp.route('/pending_bill', methods=['POST'])
def pending_bill():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    bill_no = request.form.get('bill_no')
    invoice_no = request.form.get('invoice_no')
    bill = Bill.query.filter_by(bill_no=bill_no).first()
    if bill is not None:
        bill.invoice_no = invoice_no
        db.session.add(bill)
    db.session.commit()
    flash('Invoice number added successfully!', 'success')
    return redirect(url_for('main.pending'))
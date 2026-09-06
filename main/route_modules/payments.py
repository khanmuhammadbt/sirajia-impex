from datetime import date as dt_date
from flask import flash, redirect, render_template, request, session, url_for
from sqlalchemy import func, update
from extensions import db
from model.data import company_data, data, payment_data
from .. import main_bp

def _parse_credit_date(value):
    if not value:
        return None
    for date_format in ('%Y-%m-%d', '%d-%m-%Y'):
        try:
            return dt_date.strptime(value, date_format)
        except ValueError:
            continue
    raise ValueError('Invalid credit-term date')

@main_bp.route('/credit_terms')
def credit_terms():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    return render_template('credit _terms.html', company_names=company_data.query.all())

@main_bp.route('/add_credit_terms', methods=['POST'])
def add_credit_terms():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    company_name = request.form.get('company_name')
    check_no = request.form.get('check_no')
    payment = request.form.get('payment')
    given_date = request.form.get('given_date')
    clear_date = request.form.get('clear_date')
    company = company_data.query.filter_by(name=company_name).first()
    if company is None:
        flash('Company not found.', 'danger')
        return redirect(url_for('main.credit_terms'))
    try:
        given_date_value = _parse_credit_date(given_date)
        clear_date_value = _parse_credit_date(clear_date)
    except ValueError:
        flash('Please enter valid credit-term dates.', 'danger')
        return redirect(url_for('main.credit_terms'))
    new_payment = payment_data(company_id=company.id, check_no=check_no, payment=float(payment), given_date=given_date_value, clear_date=clear_date_value)
    db.session.add(new_payment)
    db.session.commit()
    flash('Payment details saved successfully!', 'success')
    payment = float(payment)
    payment_status = data.query.filter(data.company_id == company.id, data.payment_status.in_(['unpaid', 'partial'])).group_by(data.bill_no).order_by(func.min(data.id)).all()
    overpayment_item = payment_status[-1] if payment_status else data.query.filter(data.company_id == company.id).order_by(data.id.desc()).first()
    last_applied_amount = 0
    for item in payment_status:
        bill_total = float(item.final_total or 0)
        already_paid = float(item.paid_amount or 0) if item.payment_status == 'partial' else 0
        bill_due = max(bill_total - already_paid, 0)
        applied_amount = min(payment, bill_due)
        if applied_amount <= 0:
            break
        if new_payment.bill_id is None:
            new_payment.bill_id = item.id
        payment -= applied_amount
        last_applied_amount = applied_amount
        values = {'clear_date': clear_date_value, 'check_no': check_no, 'payment': applied_amount}
        if applied_amount >= bill_due:
            values.update(payment_status='paid', paid_amount=bill_total)
        else:
            values.update(payment_status='partial', paid_amount=already_paid + applied_amount)
        db.session.execute(update(data).where(data.id == item.id).values(**values))
    if payment > 0 and overpayment_item:
        if new_payment.bill_id is None:
            new_payment.bill_id = overpayment_item.id
        db.session.execute(update(data).where(data.id == overpayment_item.id).values(payment_status='paid', paid_amount=float(overpayment_item.paid_amount or 0) + last_applied_amount + payment, payment=float(overpayment_item.payment or 0) + last_applied_amount + payment, clear_date=clear_date_value, check_no=check_no))
    db.session.commit()
    return redirect(url_for('main.credit_terms'))
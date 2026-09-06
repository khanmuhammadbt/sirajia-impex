from datetime import datetime

from extensions import db


class Seller(db.Model):
    __tablename__ = 'seller'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(100), nullable=False, unique=True, index=True)
    bills = db.relationship('Bill', back_populates='seller', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
        }


class Bill(db.Model):
    __tablename__ = 'bill'

    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('seller.id'), nullable=True, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=True, index=True)
    bill_no = db.Column(db.Integer, nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow, index=True)
    po = db.Column(db.String(100), nullable=True)
    dc = db.Column(db.String(100), nullable=True)
    order_no = db.Column(db.String(100), nullable=True)
    invoice_no = db.Column(db.String(255), nullable=True, index=True)
    tax = db.Column(db.Float, nullable=True)
    payment_status = db.Column(db.String(50), nullable=True, default='unpaid', index=True)
    paid_amount = db.Column(db.Float, nullable=True, default=0.0)
    sales_tax = db.Column(db.Float, nullable=True)
    grand_total = db.Column(db.Float, nullable=True)
    final_total = db.Column(db.Float, nullable=True)
    check_no = db.Column(db.String(100), nullable=True, index=True)
    clear_date = db.Column(db.Date, nullable=True, index=True)
    gate_pass_no = db.Column(db.String(100), nullable=True, index=True)
    payment = db.Column(db.Float, nullable=True)

    seller = db.relationship('Seller', back_populates='bills')
    company = db.relationship('Company', back_populates='bills')
    items = db.relationship('BillItem', back_populates='bill', cascade='all, delete-orphan')
    payments = db.relationship('Payment', back_populates='bill')

    __table_args__ = (
        db.Index('ix_bill_company_bill_no', 'company_id', 'bill_no'),
    )

    @property
    def company_name(self):
        return self.company.name if self.company else None

    @company_name.setter
    def company_name(self, value):
        if self.company is None:
            from .company import Company
            self.company = Company(name=value)
        else:
            self.company.name = value

    @property
    def ledger_check_no(self):
        return self.check_no or ''

    @property
    def total_amount(self):
        return sum(item.amount for item in self.items)

    def to_dict(self, include_items=False):
        result = {
            'id': self.id,
            'seller_id': self.seller_id,
            'company_id': self.company_id,
            'company_name': self.company_name,
            'bill_no': self.bill_no,
            'date': self.date.isoformat() if self.date else None,
            'po': self.po,
            'dc': self.dc,
            'order_no': self.order_no,
            'invoice_no': self.invoice_no,
            'payment_status': self.payment_status,
            'paid_amount': self.paid_amount,
            'tax': self.tax,
            'sales_tax': self.sales_tax,
            'grand_total': self.grand_total,
            'final_total': self.final_total,
            'check_no': self.check_no,
            'clear_date': self.clear_date.isoformat() if self.clear_date else None,
            'gate_pass_no': self.gate_pass_no,
            'payment': self.payment,
            'total_amount': self.total_amount,
        }
        if include_items:
            result['items'] = [item.to_dict() for item in self.items]
        return result


class BillItem(db.Model):
    __tablename__ = 'bill_item'

    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    description = db.Column(db.String(255), nullable=False, index=True)
    quantity = db.Column(db.Float, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Float, nullable=False)

    bill = db.relationship('Bill', back_populates='items')

    def to_dict(self):
        return {
            'id': self.id,
            'bill_id': self.bill_id,
            'description': self.description,
            'quantity': self.quantity,
            'rate': self.rate,
            'amount': self.amount,
        }


data = Bill

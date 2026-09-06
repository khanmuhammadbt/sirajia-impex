from datetime import datetime

from extensions import db


class Payment(db.Model):
    __tablename__ = 'payment'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False, index=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=True, index=True)
    check_no = db.Column(db.String(100), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow, index=True)
    given_date = db.Column(db.Date, nullable=False, index=True)
    clear_date = db.Column(db.Date, nullable=True, index=True)
    payment = db.Column(db.Float, nullable=False)

    company = db.relationship('Company', back_populates='payments')
    bill = db.relationship('Bill', back_populates='payments')

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'bill_id': self.bill_id,
            'check_no': self.check_no,
            'given_date': self.given_date.isoformat() if self.given_date else None,
            'clear_date': self.clear_date.isoformat() if self.clear_date else None,
            'payment': self.payment,
        }


payment_data = Payment

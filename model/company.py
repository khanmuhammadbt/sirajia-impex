from extensions import db


class Company(db.Model):
    __tablename__ = 'company'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True, index=True)
    company_name = db.synonym('name')
    address = db.Column(db.String(255), nullable=True)
    ntn = db.Column(db.String(100), nullable=True)
    gst = db.Column(db.String(100), nullable=True)
    payment_days = db.Column(db.Integer, nullable=False, default=0)

    bills = db.relationship('Bill', back_populates='company', cascade='all, delete-orphan')
    payments = db.relationship('Payment', back_populates='company', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'ntn': self.ntn,
            'gst': self.gst,
            'payment_days': self.payment_days,
        }


company_data = Company

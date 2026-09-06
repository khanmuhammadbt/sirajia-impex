from extensions import db


class Setting(db.Model):
    __tablename__ = 'setting'

    id = db.Column(db.Integer, primary_key=True)
    sales_tax = db.Column(db.Float, nullable=True, default=0.0)


setting = Setting

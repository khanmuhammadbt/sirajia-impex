from datetime import date, datetime, time, timedelta

from app import app
from extensions import db
from model.data import Bill, BillItem, Company, Payment


COMPANY_NAME = 'Ledger Demo Company'


def seed_ledger_data():
    with app.app_context():
        company = Company.query.filter_by(name=COMPANY_NAME).first()
        if company is None:
            company = Company(name=COMPANY_NAME, address='Ledger demo address')
            db.session.add(company)
            db.session.flush()

        if Bill.query.filter_by(company_id=company.id, bill_no=9001).first():
            print('Ledger demo data already exists.')
            return

        base_time = datetime.combine(date.today(), time(10, 1))
        bill_values = [
            (9001, 100.0, 0),
            (9002, 100.0, 2),
            (9003, 100.0, 4),
            (9004, 100.0, 6),
        ]

        for bill_no, total, minute_offset in bill_values:
            bill = Bill(
                company=company,
                bill_no=bill_no,
                date=date.today(),
                created_at=base_time + timedelta(minutes=minute_offset),
                payment_status='unpaid',
                paid_amount=0.0,
                grand_total=total,
                final_total=total,
                tax=0.0,
                sales_tax=0.0,
            )
            bill.items = [BillItem(
                description=f'Ledger demo item {bill_no}',
                quantity=1,
                rate=total,
                amount=total,
            )]
            db.session.add(bill)

        for number, minute_offset in enumerate((1, 3, 7, 9), start=1):
            db.session.add(Payment(
                company=company,
                check_no=f'LEDGER-DEMO-{number}',
                given_date=date.today(),
                clear_date=date.today(),
                payment=25.0,
                created_at=base_time + timedelta(minutes=minute_offset),
            ))

        db.session.commit()
        print('Ledger demo data created.')
        print('Order: Bill 9001, Payment 1, Bill 9002, Payment 2, Bill 9003, Bill 9004, Payment 3, Payment 4')
        print('Expected balances: 100, 75, 175, 150, 250, 350, 325, 300')


if __name__ == '__main__':
    seed_ledger_data()

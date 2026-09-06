from datetime import date, timedelta

from app import app
from extensions import db
from model.data import Bill, BillItem, Company, Payment, Seller, Setting


COMPANIES = [
    {
        'name': 'Al Noor Traders',
        'address': '12 Market Road, Lahore',
        'ntn': '1234567-8',
        'gst': 'GST-ALN-001',
        'payment_days': 30,
    },
    {
        'name': 'PakBuild Supplies',
        'address': '45 Industrial Estate, Karachi',
        'ntn': '7654321-2',
        'gst': 'GST-PBS-002',
        'payment_days': 45,
    },
    {
        'name': 'GreenField Hardware',
        'address': '8 Canal View, Islamabad',
        'ntn': '2468135-7',
        'gst': 'GST-GFH-003',
        'payment_days': 15,
    },
]

SELLERS = [
    {'name': 'Muhammad Imran', 'code': 'SAL-001'},
    {'name': 'Ayesha Khan', 'code': 'SAL-002'},
]

BILLS = [
    {
        'company': 'Al Noor Traders',
        'seller': 'SAL-001',
        'bill_no': 1001,
        'date': date.today() - timedelta(days=18),
        'invoice_no': 'INV-1001',
        'payment_status': 'paid',
        'paid_amount': 74200.0,
        'check_no': 'CHK-DEMO-001',
        'clear_date': date.today() - timedelta(days=8),
        'gate_pass_no': 'GP-1001',
        'tax_rate': 17.0,
        'items': [
            ('Cement bags', 100, 650.0),
            ('Binding wire', 20, 470.0),
        ],
    },
    {
        'company': 'PakBuild Supplies',
        'seller': 'SAL-002',
        'bill_no': 1002,
        'date': date.today() - timedelta(days=9),
        'invoice_no': 'INV-1002',
        'payment_status': 'partial',
        'paid_amount': 25000.0,
        'check_no': 'CHK-DEMO-002',
        'clear_date': date.today() - timedelta(days=2),
        'gate_pass_no': 'GP-1002',
        'tax_rate': 17.0,
        'items': [
            ('PVC pipes, 1 inch', 50, 420.0),
            ('Pipe elbows', 40, 85.0),
        ],
    },
    {
        'company': 'GreenField Hardware',
        'seller': 'SAL-001',
        'bill_no': 1003,
        'date': date.today() - timedelta(days=3),
        'invoice_no': None,
        'payment_status': 'unpaid',
        'paid_amount': 0.0,
        'tax_rate': 17.0,
        'items': [
            ('LED flood light', 12, 1850.0),
            ('Electrical cable roll', 5, 3200.0),
        ],
    },
]


def seed_data():
    with app.app_context():
        for values in COMPANIES:
            company = Company.query.filter_by(name=values['name']).first()
            if company is None:
                db.session.add(Company(**values))

        for values in SELLERS:
            seller = Seller.query.filter_by(code=values['code']).first()
            if seller is None:
                db.session.add(Seller(**values))

        db.session.flush()

        for values in BILLS:
            company = Company.query.filter_by(name=values['company']).one()
            seller = Seller.query.filter_by(code=values['seller']).one()
            bill = Bill.query.filter_by(company_id=company.id, bill_no=values['bill_no']).first()
            if bill is not None:
                for field in ('check_no', 'clear_date', 'gate_pass_no'):
                    if getattr(bill, field) is None and values.get(field) is not None:
                        setattr(bill, field, values[field])
                if not bill.tax and bill.items:
                    subtotal = sum(item.amount for item in bill.items)
                    tax_amount = subtotal * values['tax_rate'] / 100
                    bill.tax = tax_amount
                    bill.sales_tax = values['tax_rate']
                    bill.grand_total = subtotal
                    bill.final_total = subtotal + tax_amount
                continue

            items = values['items']
            total = sum(quantity * rate for _, quantity, rate in items)
            tax_amount = total * values['tax_rate'] / 100
            bill = Bill(
                company=company,
                seller=seller,
                bill_no=values['bill_no'],
                date=values['date'],
                invoice_no=values['invoice_no'],
                payment_status=values['payment_status'],
                paid_amount=values['paid_amount'],
                grand_total=total,
                final_total=total + tax_amount,
                tax=tax_amount,
                sales_tax=values['tax_rate'],
                check_no=values.get('check_no'),
                clear_date=values.get('clear_date'),
                gate_pass_no=values.get('gate_pass_no'),
            )
            bill.items = [
                BillItem(
                    description=description,
                    quantity=quantity,
                    rate=rate,
                    amount=quantity * rate,
                )
                for description, quantity, rate in items
            ]
            db.session.add(bill)

        company = Company.query.filter_by(name='Al Noor Traders').one()
        if not Payment.query.filter_by(company_id=company.id, check_no='CHK-DEMO-001').first():
            db.session.add(Payment(
                company=company,
                check_no='CHK-DEMO-001',
                given_date=date.today() - timedelta(days=12),
                clear_date=date.today() - timedelta(days=8),
                payment=74200.0,
            ))

        if Setting.query.first() is None:
            db.session.add(Setting(sales_tax=17.0))

        db.session.commit()
        print('Dummy data is ready.')
        print(f'Companies: {Company.query.count()}')
        print(f'Sellers: {Seller.query.count()}')
        print(f'Bills: {Bill.query.count()}')
        print(f'Bill items: {BillItem.query.count()}')
        print(f'Payments: {Payment.query.count()}')
        print(f'Settings: {Setting.query.count()}')


if __name__ == '__main__':
    seed_data()

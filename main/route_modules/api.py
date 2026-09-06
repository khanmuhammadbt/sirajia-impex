from datetime import date as dt_date
from flask import jsonify, request
from sqlalchemy import func
from extensions import db
from model.data import Bill, BillItem, Seller
from .. import main_bp

@main_bp.route('/api/sellers', methods=['POST'])
def create_seller():
    payload = request.get_json(silent=True) or {}
    name, code = payload.get('name'), payload.get('code')
    if not name or not code:
        return jsonify({'error': 'name and code are required'}), 400
    if Seller.query.filter_by(code=code).first():
        return jsonify({'error': 'seller code already exists'}), 409
    seller = Seller(name=name, code=code)
    db.session.add(seller)
    db.session.commit()
    return jsonify(seller.to_dict()), 201

@main_bp.route('/api/sellers', methods=['GET'])
def list_sellers():
    return jsonify([seller.to_dict() for seller in Seller.query.order_by(Seller.id.asc()).all()]), 200

@main_bp.route('/api/sellers/<int:seller_id>', methods=['GET'])
def get_seller(seller_id):
    return jsonify(Seller.query.get_or_404(seller_id).to_dict()), 200

@main_bp.route('/api/sellers/<int:seller_id>', methods=['PUT'])
def update_seller(seller_id):
    seller = Seller.query.get_or_404(seller_id)
    payload = request.get_json(silent=True) or {}
    name, code = payload.get('name'), payload.get('code')
    if name is not None:
        seller.name = name
    if code is not None:
        existing = Seller.query.filter(Seller.code == code, Seller.id != seller_id).first()
        if existing:
            return jsonify({'error': 'seller code already exists'}), 409
        seller.code = code
    db.session.commit()
    return jsonify(seller.to_dict()), 200

@main_bp.route('/api/sellers/<int:seller_id>', methods=['DELETE'])
def delete_seller(seller_id):
    db.session.delete(Seller.query.get_or_404(seller_id))
    db.session.commit()
    return jsonify({'message': 'seller deleted'}), 200

@main_bp.route('/api/bills', methods=['POST'])
def create_bill():
    payload = request.get_json(silent=True) or {}
    seller_id, bill_date_raw, items_payload = payload.get('seller_id'), payload.get('date'), payload.get('items', [])
    if not seller_id or not bill_date_raw:
        return jsonify({'error': 'seller_id and date are required'}), 400
    seller = Seller.query.get(seller_id)
    if not seller:
        return jsonify({'error': 'seller not found'}), 404
    if not isinstance(items_payload, list) or len(items_payload) == 0:
        return jsonify({'error': 'items must be a non-empty list'}), 400
    try:
        bill_date = dt_date.fromisoformat(bill_date_raw)
    except ValueError:
        return jsonify({'error': 'date must be in YYYY-MM-DD format'}), 400
    max_bill_no = db.session.query(func.max(Bill.bill_no)).filter(Bill.seller_id == seller_id).scalar()
    bill = Bill(seller_id=seller_id, bill_no=(max_bill_no or 0) + 1, date=bill_date)
    for raw_item in items_payload:
        description, quantity, rate = raw_item.get('description'), raw_item.get('quantity'), raw_item.get('rate')
        if not description or quantity is None or rate is None:
            return jsonify({'error': 'each item needs description, quantity, rate'}), 400
        try:
            quantity_val, rate_val = float(quantity), float(rate)
        except (TypeError, ValueError):
            return jsonify({'error': 'quantity and rate must be numeric'}), 400
        bill.items.append(BillItem(description=description, quantity=quantity_val, rate=rate_val, amount=quantity_val * rate_val))
    db.session.add(bill)
    db.session.commit()
    return jsonify(bill.to_dict(include_items=True)), 201

@main_bp.route('/api/bills/<int:bill_id>', methods=['GET'])
def get_bill(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    response = bill.to_dict(include_items=True)
    response['seller'] = bill.seller.to_dict()
    return jsonify(response), 200

@main_bp.route('/api/sellers/<int:seller_id>/bills', methods=['GET'])
def list_bills_for_seller(seller_id):
    seller = Seller.query.get_or_404(seller_id)
    bills = Bill.query.filter_by(seller_id=seller.id).order_by(Bill.bill_no.asc()).all()
    return jsonify({'seller': seller.to_dict(), 'bills': [bill.to_dict(include_items=True) for bill in bills]}), 200

@main_bp.route('/api/bills/<int:bill_id>', methods=['DELETE'])
def delete_bill(bill_id):
    db.session.delete(Bill.query.get_or_404(bill_id))
    db.session.commit()
    return jsonify({'message': 'bill deleted'}), 200
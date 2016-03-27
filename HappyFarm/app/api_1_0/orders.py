# -*- coding:utf-8 -*-
from . import api
from app.models import Order, Store, User
from flask import jsonify

#实现资源端点
@api.route('/orders')
def get_orders():
    orders = Order.query.all()
    return jsonify({'orders':[order.to_json() for order in orders]})

@api.route('/order/<int:id>')
def get_order(id):
    order = Order.query.get_or_404(id)
    return jsonify(order.to_json())  



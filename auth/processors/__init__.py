import sys

from auth.models import Order, Processor, Transaction, Voucher
from auth.services import db
from auth.utils import render_currency_amount
from flask import current_app, flash
from flask_security import current_user


def init_processors(app):
    cash.init_app(app)

    if app.config.get('PAYU_SAFEKEY'):
        payu.init_app(app)

    if app.config.get('SNAPSCAN_API_KEY'):
        snapscan.init_app(app)


def get_processor(id):
    return getattr(sys.modules[__name__], id)


def flash_transaction(transaction):
    order = transaction.order
    if order.owed_amount == 0:
        flash('Paid %s' % order)
    else:
        flash('Still owed %s on %s' % ( render_currency_amount(order.currency, order.owed_amount), order), 'warning')


def update_transaction(id, response):
    processor = Processor.query.get_or_404(id)
    processor_module = get_processor(id)
    order_param = processor_module.get_order_param()
    merchant_reference = processor_module.get_merchant_reference(response)
    order = Order.query.filter_by(**{order_param: merchant_reference}).first_or_404()
    processor_reference = processor_module.get_processor_reference(response)
    transaction = processor.transactions.filter_by(processor_reference=processor_reference).first()

    if transaction is None:
        transaction = Transaction()
        transaction.tip_amount = processor_module.get_tip_amount(response)
        transaction.total_amount = processor_module.get_transaction_amount(response)
        transaction.currency_id = processor_module.get_transaction_currency(response)
        transaction.processor = processor
        transaction.processor_reference = processor_reference
        if current_user.is_authenticated:
            transaction.user_id = current_user.id
        transaction.type = processor_module.transaction_types[processor_module.get_transaction_type(response)]
        order.transactions.append(transaction)

    transaction.status = processor_module.transaction_statuses[processor_module.get_transaction_status(response)]

    order.calculate_totals()

    if order.status == 'new' and order.owed_amount == 0:
        order.status = 'paid'

        for item in order.items:
            if item.product.category.code == 'vouchers':
                for index in range(int(item.quantity)):
                    voucher = Voucher()
                    voucher.minutes = item.product.minutes
                    voucher.megabytes = item.product.megabytes
                    order.gateway.vouchers.append(voucher)
                    order.vouchers.append(voucher)

    db.session.commit()


    return transaction

from auth.processors import cash, payu, snapscan

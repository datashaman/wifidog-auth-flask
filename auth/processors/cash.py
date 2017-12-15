from __future__ import absolute_import

from auth.forms import instances
from auth.processors import flash_transaction, update_transaction
from auth.utils import generate_uuid
from flask import Blueprint, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import FloatField
from wtforms.ext.sqlalchemy.fields import QuerySelectField

bp = Blueprint('cash', __name__)

transaction_types = {
    'payment': 'payment'
}

transaction_statuses = {
    'successful': 'successful',
}


class CashForm(FlaskForm):
    currency = QuerySelectField('Currency', query_factory=instances('currency'))
    cash = FloatField('Cash')


def init_app(app):
    app.register_blueprint(bp)


def pay_order(order):
    form = CashForm()
    if form.validate_on_submit():
        response = {
            'amount': max(float(form.cash.data), order.owed_amount),
            'currency': form.currency.data.id,
            'hash': generate_uuid(),
            'merchant_reference': order.id,
        }
        transaction = update_transaction('cash', response)
        flash_transaction(transaction)
        return redirect(url_for('.order_index'))
    return render_template('order/cash.html', form=form, order=order)


def get_merchant_reference(response):
    return response['merchant_reference']


def get_processor_reference(response):
    return response['hash']


def get_tip_amount(response):
    # TODO Think about how to do this
    return 0


def get_transaction_amount(response):
    return response['amount']


def get_transaction_currency(response):
    return response['currency']


def get_transaction_status(response):
    return 'successful'


def get_transaction_type(response):
    return 'payment'

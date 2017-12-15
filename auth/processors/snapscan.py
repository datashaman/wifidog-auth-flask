from __future__ import absolute_import

import simplejson as json
import requests

from auth.models import db
from auth.processors import update_transaction
from flask import Blueprint, current_app, redirect, request
from flask_security import current_user


bp = Blueprint('snapscan', __name__)
session = None

transaction_types = {
    'payment': 'payment'
}

transaction_statuses = {
    'pending': 'processing',
    'completed': 'successful',
    'error': 'failed',
}


def init_app(app):
    global session
    session = requests.Session()
    session.auth = (app.config['SNAPSCAN_API_KEY'], '')
    app.register_blueprint(bp)


def pay_order(order):
    return redirect('https://pos.snapscan.io/qr/%s?id=%s&amount=%d&strict=true' % \
                    (current_app.config['SNAPSCAN_SNAP_CODE'],
                     order.hash,
                     int(order.owed_amount * 100)))


def get_transaction(id):
    response = session.get('%s/payments/%d' % (current_app.config['SNAPSCAN_ENDPOINT'], id))
    return response.json()


def get_merchant_reference(response):
    return response['merchantReference']


def get_processor_reference(response):
    return response['id']


def get_tip_amount(response):
    return response['tipAmount'] / 100


def get_transaction_amount(response):
    return response['totalAmount'] / 100


def get_transaction_currency(response):
    return 'ZAR'


def get_transaction_status(response):
    return response['status']


def get_transaction_type(response):
    return 'payment'


@bp.route('/snapscan/notification', methods=['POST'])
def snapscan_notification():
    payload = json.loads(request.form.get('payload'))
    response = get_transaction(payload['id'])
    update_transaction('snapscan', response)
    return 'OK'

from __future__ import absolute_import

import suds_requests

from auth.processors import flash_transaction, update_transaction
from flask import Blueprint, current_app, redirect, request, url_for
from flask_security import current_user
from suds.client import Client
from suds.plugin import MessagePlugin
from suds.wsse import Security, UsernameToken

api = 'ONE_ZERO'
bp = Blueprint('payu', __name__)

transaction_statuses = {
    'NEW': 'new',
    'PROCESSING': 'processing',
    'SUCCESSFUL': 'successful',
    'FAILED': 'failed',
}

transaction_types = {
    'PAYMENT': 'payment',
}


class PayUPlugin(MessagePlugin):
    """Add the required attributes and namespaces for PayU to recognize the request."""
    def marshalled(self, context):
        username_token = context.envelope.childAtPath('Header/wsse:Security/wsse:UsernameToken')
        username_token.getChild('wsse:Password').set('Type', 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText')


client = None


def init_app(app):
    global client

    client = Client(app.config['PAYU_WSDL'],
                    plugins=[PayUPlugin()],
                    transport=suds_requests.RequestsTransport())
    security = Security()
    token = UsernameToken(app.config['PAYU_USERNAME'], app.config['PAYU_PASSWORD'])
    security.tokens.append(token)
    client.set_options(wsse=security)
    app.register_blueprint(bp)


def pay_order(order):
    response = client.service.setTransaction(
        Api=api,
        Safekey=current_app.config['PAYU_SAFEKEY'],
        TransactionType='PAYMENT',
        AdditionalInformation=dict(
            cancelUrl=url_for('payu.payu_cancel',  _external=True),
            merchantReference=order.id,
            notificationUrl=url_for('payu.payu_notification', _external=True),
            returnUrl=url_for('payu.payu_return', _external=True),
            supportedPaymentMethods='CREDITCARD',
        ),
        Basket=dict(
            amountInCents=int(order.total * 100),
            currencyCode=order.currency.id,
        ),
        Customer=dict(
            firstName=order.user.first_name,
            lastName=order.user.last_name,
            mobile=order.user.mobile,
            email=order.user.email,
            merchantUserId=order.user.id,
        ),
    )

    return redirect('%s?PayUReference=%s' % (current_app.config['PAYU_URL'],
                    response.payUReference))


def get_transaction(payUReference):
    return client.service.getTransaction(
        Api=api,
        Safekey=current_app.config['PAYU_SAFEKEY'],
        AdditionalInformation={
            'payUReference': payUReference
        }
    )


def get_merchant_reference(response):
    return response.merchantReference


def get_processor_reference(response):
    return response.payUReference


def get_transaction_amount(response):
    return int(response.basket.amountInCents) / 100


def get_transaction_currency(response):
    return response.basket.currencyCode


def get_transaction_status(response):
    return response.transactionState


def get_transaction_type(response):
    return response.transactionType


@bp.route('/payu/return')
def payu_return():
    response = get_transaction(request.args.get('PayUReference'))
    transaction = update_transaction('payu', current_user, response)
    flash_transaction(transaction)
    return redirect(url_for('auth.transaction_show', hash=transaction.hash))


@bp.route('/payu/cancel')
def payu_cancel():
    response = get_transaction(request.args.get('PayUReference'))
    transaction = update_transaction('payu', current_user, response)
    flash_transaction(transaction)
    return redirect(url_for('auth.transaction_show', hash=transaction.hash))


@bp.route('/payu/notification')
def payu_notification():
    pass

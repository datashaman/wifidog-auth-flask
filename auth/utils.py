from __future__ import absolute_import

import uuid

from flask import request, current_app
from flask_security import current_user


def is_logged_out():
    return not current_user.is_authenticated


def is_logged_in():
    return current_user.is_authenticated


def has_role(*roles):
    def func():
        if current_user.is_authenticated:
            for role in roles:
                if current_user.has_role(role):
                    return True
        return False
    return func


def args_get(which):
    def func():
        value = request.args.get(which)
        if value == '':
            value = None
        return value
    return func


def render_currency_amount(currency, amount):
    if amount is None:
        return 'None'

    return '%s%.2f%s' % (currency.prefix or '',
                         amount,
                         currency.suffix or '')


def generate_token():
    """Generate token for the voucher session"""
    return uuid.uuid4().hex

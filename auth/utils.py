from __future__ import absolute_import

import base64
import random
import re
import string
import uuid

from flask import request
from flask_security import current_user
from random import choice


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

    return '%s%.2f%s' % (currency.prefix if currency.prefix else '',
                       amount,
                       currency.suffix if currency.suffix else '')


chars = string.ascii_lowercase + string.digits


def generate_code(input_length=4):
    source = ''.join(choice(chars) for _ in range(input_length))
    encoded = base64.b32encode(source.encode()).decode()
    result = re.sub(r'=*$', '', encoded)
    return result


def generate_order_hash():
    return str(uuid.uuid1())


def generate_uuid():
    return str(uuid.uuid4())

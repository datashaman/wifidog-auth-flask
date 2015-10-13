from app.utils import args_get
from flask import current_app
from flask.ext.wtf import Form
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms import HiddenField, PasswordField, TextField, TextAreaField, IntegerField, SelectField, validators

from app.models import Network, Voucher

import constants

def default_minutes():
    return current_app.config.get('VOUCHER_DEFAULT_MINUTES')

class NewVoucherForm(Form):
    gateway_id = SelectField('Gateway')
    minutes = IntegerField('Minutes', [ validators.InputRequired(), validators.NumberRange(min=0) ], default=default_minutes)

class BroadcastForm(Form):
    message = TextField('Message', [ validators.InputRequired() ])

class LoginVoucherForm(Form):
    voucher = TextField('Voucher', [ validators.InputRequired() ], default=args_get('voucher'))
    email = TextField('Email Address', [ validators.InputRequired(), validators.Email() ])

    gw_address = HiddenField('Gateway Address', default=args_get('gw_address'))
    gw_port = HiddenField('Gateway Port', default=args_get('gw_port'))
    gateway_id = HiddenField('Gateway ID', default=args_get('gw_id'))
    mac = HiddenField('MAC', default=args_get('mac'))
    url = HiddenField('URL', default=args_get('url'))

    def validate_voucher(form, field):
        voucher = Voucher.query.get(field.data)

        if voucher is None:
            raise validators.ValidationError('Voucher does not exist')

        if voucher.started_at is not None:
            raise validators.ValidationError('Voucher is in use')

class NetworkForm(Form):
    id = TextField('ID', [ validators.InputRequired() ])

    title = TextField('Title', [ validators.InputRequired(), validators.Length(min=5, max=20) ])
    description = TextAreaField('Description', [ validators.InputRequired() ])

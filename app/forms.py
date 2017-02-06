from app.utils import args_get
from flask import current_app
from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms import HiddenField, PasswordField, StringField, TextAreaField, IntegerField, SelectField, validators

from app.models import Network, Voucher

import constants

def default_minutes():
    return current_app.config.get('VOUCHER_DEFAULT_MINUTES')

class NewVoucherForm(FlaskForm):
    gateway_id = SelectField('Gateway')
    minutes = IntegerField('Minutes', [ validators.InputRequired(), validators.NumberRange(min=0) ], default=default_minutes)

class BroadcastForm(FlaskForm):
    message = StringField('Message', [ validators.InputRequired() ])

class LoginVoucherForm(FlaskForm):
    voucher_code = StringField('Voucher Code', [ validators.InputRequired() ], default=args_get('voucher'), description='The voucher code you were given at the counter')
    name = StringField('Your Name', description='So we know what to call you')

    gw_address = HiddenField('Gateway Address', default=args_get('gw_address'))
    gw_port = HiddenField('Gateway Port', default=args_get('gw_port'))
    gateway_id = HiddenField('Gateway ID', default=args_get('gw_id'))
    mac = HiddenField('MAC', default=args_get('mac'))
    url = HiddenField('URL', default=args_get('url'))

    def validate_voucher(form, field):
        voucher_code = field.data.upper()
        voucher = Voucher.query.filter_by(code=voucher_code).first()

        if voucher is None:
            raise validators.ValidationError('Voucher does not exist')

        if voucher.status != 'new':
            raise validators.ValidationError('Voucher is %s' % voucher.status)

class NetworkForm(FlaskForm):
    id = StringField('ID', [ validators.InputRequired() ])

    title = StringField('Title', [ validators.InputRequired(), validators.Length(min=5, max=20) ])
    description = TextAreaField('Description', [ validators.InputRequired() ])

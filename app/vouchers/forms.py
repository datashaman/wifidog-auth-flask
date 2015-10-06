from app.utils import args_get
from wtforms import Form, HiddenField, PasswordField, TextField, validators

from app.vouchers.models import Voucher

class VoucherForm(Form):
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

from __future__ import absolute_import

from app.utils import args_get
from flask import current_app
from flask_security import current_user
from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, PasswordField, StringField, IntegerField, SelectField, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.ext.sqlalchemy.orm import model_form

from app.models import db, Category, Country, Currency, Gateway, Network, Product, Voucher, Role
from app.resources import api

def default_minutes():
    return current_app.config.get('VOUCHER_DEFAULT_MINUTES')

def instances(resource):
    def func():
        return api.resources[resource].manager.instances()
    return func

def roles():
    if current_user.has_role(u'super-admin'):
        return db.session.query(Role).all()
    if current_user.has_role(u'network-admin'):
        return db.session.query(Role).filter(Role.name == u'gateway-admin').all()
    return []

CategoryForm = model_form(
    Category,
    db.session,
    FlaskForm,
    exclude=[
        'children',
        'created_at',
        'products',
        'status',
        'sub_categories',
        'updated_at',
    ],
    field_args={
        'gateway': {
            'default': lambda: current_user.gateway,
            'query_factory': instances('gateways'),
        },
        'network': {
            'default': lambda: current_user.network,
            'query_factory': instances('networks'),
        }
    }
)
CountryForm = model_form(
    Country,
    db.session,
    FlaskForm,
    exclude=[
        'created_at',
        'updated_at',
    ],
    exclude_pk=False
)
CurrencyForm = model_form(
    Currency,
    db.session,
    FlaskForm,
    exclude=[
        'created_at',
        'orders',
        'products',
        'updated_at',
    ],
    exclude_pk=False
)
GatewayForm = model_form(
    Gateway,
    db.session,
    FlaskForm,
    exclude=[
        'auths',
        'created_at',
        'categories',
        'orders',
        'pings',
        'products',
        'updated_at',
        'users',
        'vouchers',
    ],
    exclude_pk=False,
    field_args={
        'network': {
            'default': lambda: current_user.network,
            'query_factory': instances('networks'),
        }
    }
)
NetworkForm = model_form(
    Network,
    db.session,
    FlaskForm,
    exclude=[
        'categories',
        'created_at',
        'gateways',
        'orders',
        'products',
        'updated_at',
        'users',
    ],
    exclude_pk=False
)
ProductForm = model_form(
    Product,
    db.session,
    FlaskForm,
    exclude=[
        'categories',
        'created_at',
        'order_items',
        'updated_at',
    ],
    field_args={
        'gateway': {
            'default': lambda: current_user.gateway,
            'query_factory': instances('gateways'),
        },
        'network': {
            'default': lambda: current_user.network,
            'query_factory': instances('networks'),
        }
    }
)

class UserForm(FlaskForm):
    network = QuerySelectField('Network', allow_blank=True, default=lambda: current_user.network, query_factory=instances('networks'))
    gateway = QuerySelectField('Gateway', allow_blank=True, default=lambda: current_user.gateway, query_factory=instances('gateways'))
    email = StringField('Email', description='Your email address')
    password = PasswordField(
        'Password',
        [
            validators.Optional(),
            validators.Length(min=2),
            validators.EqualTo('confirm', message='Passwords must match'),
        ]
    )
    confirm = PasswordField('Repeat Password')
    active = BooleanField('Active')
    roles = QuerySelectMultipleField('Roles', query_factory=roles)

class MyUserForm(FlaskForm):
    email = StringField('Email', description='Your email address')
    password = PasswordField(
        'Password',
        [
            validators.Optional(),
            validators.Length(min=2),
            validators.EqualTo('confirm', message='Passwords must match'),
        ]
    )
    confirm = PasswordField('Repeat Password')

class NewVoucherForm(FlaskForm):
    gateway_id = SelectField('Gateway')
    minutes = IntegerField('Minutes', [ validators.InputRequired(), validators.NumberRange(min=0) ], default=default_minutes)
    megabytes = IntegerField('Megabytes', [ validators.Optional(), validators.NumberRange(min=0) ])

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

    def validate_voucher(self, form, field):
        voucher_code = field.data.upper()

        voucher = Voucher.query.filter_by(code=voucher_code).first()

        if voucher is None:
            raise validators.ValidationError('Voucher does not exist')

        if voucher.status != 'new':
            raise validators.ValidationError('Voucher is %s' % voucher.status)

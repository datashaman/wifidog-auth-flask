from __future__ import absolute_import

from auth.models import db, Cashup, Category, Country, Currency, Gateway, Network, Product, Voucher, Role, SqliteDecimal
from auth.resources import resource_query
from auth.utils import args_get
from flask import current_app
from flask_security import current_user
from flask_wtf import FlaskForm
from wtforms import fields as f, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.ext.sqlalchemy.orm import converts, model_form, ModelConverter as BaseModelConverter


def default_megabytes():
    if current_user.gateway is not None:
        return current_user.gateway.default_megabytes


def default_minutes():
    if current_user.gateway is not None:
        return current_user.gateway.default_minutes


def instances(resource):
    def func():
        return resource_query(resource).all()
    return func


def roles():
    if current_user.has_role('super-admin'):
        return db.session.query(Role).all()
    if current_user.has_role('network-admin'):
        return db.session.query(Role).filter(Role.name == 'gateway-admin').all()
    return []


class ModelConverter(BaseModelConverter):
    @converts('String', 'Unicode')
    def conv_String(self, field_args, **extra):
        if extra['column'].name == 'logo':
            return f.FileField(**field_args)
        else:
            return BaseModelConverter.conv_String(self, field_args, **extra)

    @converts('auth.models.SqliteDecimal')
    def conv_SqliteDecimal(self, column, field_args, **extra):
        return BaseModelConverter.handle_decimal_types(self, column, field_args, **extra)


model_converter = ModelConverter()

CashupForm = model_form(
    Cashup,
    db.session,
    FlaskForm,
    exclude=[
        'created_at',
        'transactions',
        'user',
    ]
)


CategoryForm = model_form(
    Category,
    db.session,
    FlaskForm,
    exclude=[
        'children',
        'created_at',
        'products',
        'read_only',
        'status',
        'sub_categories',
        'updated_at',
    ],
    field_args={
        'gateway': {
            'default': lambda: current_user.gateway,
            'query_factory': instances('gateway'),
        },
        'network': {
            'default': lambda: current_user.network,
            'query_factory': instances('network'),
        }
    },
    converter=model_converter
)


CountryForm = model_form(
    Country,
    db.session,
    FlaskForm,
    exclude=[
        'created_at',
        'gateways',
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
        'networks',
        'orders',
        'products',
        'updated_at',
    ],
    exclude_pk=False
)


class GatewayConverter(ModelConverter):
    @converts('String', 'Unicode')
    def conv_String(self, field_args, **extra):
        if extra['column'].name == 'logo':
            return f.FileField(**field_args)
        else:
            return ModelConverter.conv_String(self, field_args, **extra)


GatewayForm = model_form(
    Gateway,
    db.session,
    FlaskForm,
    exclude=[
        'auths',
        'cashups',
        'created_at',
        'categories',
        'orders',
        'products',
        'updated_at',
        'users',
        'vouchers',
    ],
    exclude_pk=False,
    field_args={
        'logo': {
            'description': 'Images only, resampled down to 300 x 300 pixels.',
        },
        'network': {
            'default': lambda: current_user.network,
            'query_factory': instances('network'),
        }
    },
    converter=GatewayConverter()
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


class OrderForm(FlaskForm):
    gateway = f.SelectField('Gateway', default=lambda: current_user.gateway)
    product = QuerySelectField('Product', query_factory=instances('product'))
    quantity = f.IntegerField('Quantity', default=1)
    price = f.DecimalField('Price')


ProductForm = model_form(
    Product,
    db.session,
    FlaskForm,
    exclude=[
        'created_at',
        'order_items',
        'updated_at',
    ],
    field_args={
        'gateway': {
            'default': lambda: current_user.gateway,
            'query_factory': instances('gateway'),
        },
        'network': {
            'default': lambda: current_user.network,
            'query_factory': instances('network'),
        },
    },
    converter=model_converter
)


class UserForm(FlaskForm):
    network = QuerySelectField('Network', allow_blank=True, default=lambda: current_user.network, query_factory=instances('network'))
    gateway = QuerySelectField('Gateway', allow_blank=True, default=lambda: current_user.gateway, query_factory=instances('gateway'))
    email = f.StringField('Email')
    password = f.PasswordField(
        'Password',
        [
            validators.Optional(),
            validators.Length(min=2),
            validators.EqualTo('confirm', message='Passwords must match'),
        ]
    )
    confirm = f.PasswordField('Repeat Password')
    locale = f.SelectField('Locale', default=lambda: current_app.config['BABEL_DEFAULT_LOCALE'])
    timezone = f.SelectField('Timezone', default=lambda: current_app.config['BABEL_DEFAULT_TIMEZONE'])
    active = f.BooleanField('Active', default=True)
    roles = QuerySelectMultipleField('Roles', query_factory=roles)


class MyUserForm(FlaskForm):
    email = f.StringField('Email')
    password = f.PasswordField(
        'Password',
        [
            validators.Optional(),
            validators.Length(min=2),
            validators.EqualTo('confirm', message='Passwords must match'),
        ]
    )
    confirm = f.PasswordField('Repeat Password')
    locale = f.SelectField('Locale', default=lambda: current_app.config['BABEL_DEFAULT_LOCALE'])
    timezone = f.SelectField('Timezone', default=lambda: current_app.config['BABEL_DEFAULT_TIMEZONE'])


class NewVoucherForm(FlaskForm):
    gateway_id = f.SelectField('Gateway')
    minutes = f.IntegerField('Minutes', [validators.InputRequired(), validators.NumberRange(min=0)], default=default_minutes)
    megabytes = f.IntegerField('Megabytes', [validators.Optional(), validators.NumberRange(min=0)], default=default_megabytes)


class BroadcastForm(FlaskForm):
    message = f.StringField('Message', [validators.InputRequired()])


class LoginVoucherForm(FlaskForm):
    voucher_code = f.StringField('Voucher Code', [validators.InputRequired()], default=args_get('voucher'), description='The voucher code you were given at the counter')
    name = f.StringField('Your Name', description='So we know what to call you')

    gw_address = f.HiddenField('Gateway Address', default=args_get('gw_address'))
    gw_port = f.HiddenField('Gateway Port', default=args_get('gw_port'))
    gw_id = f.HiddenField('Gateway ID', default=args_get('gw_id'))
    mac = f.HiddenField('MAC', default=args_get('mac'))
    url = f.HiddenField('URL', default=args_get('url'))

    def validate_voucher(self, form, field):
        voucher_code = field.data.upper()

        voucher = Voucher.query.filter_by(code=voucher_code).first()

        if voucher is None:
            raise validators.ValidationError('Voucher does not exist')

        if voucher.status != 'new':
            raise validators.ValidationError('Voucher is %s' % voucher.status)

class SelectCategoryForm(FlaskForm):
    category = f.SelectField('Category')

class SelectNetworkGatewayForm(FlaskForm):
    network = QuerySelectField('Network', default=lambda: current_user.network, query_factory=instances('network'))
    gateway = QuerySelectField('Gateway', allow_blank=True, default=lambda: current_user.gateway, query_factory=instances('gateway'))

from __future__ import absolute_import

from auth.graphs import graphs
from auth.models import db, Adjustment, Cashup, Category, Country, Currency, Gateway, GatewayType, Network, Order, Product, Role, SqliteDecimal, Transaction, Voucher
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

AdjustmentForm = model_form(
    Adjustment,
    db.session,
    FlaskForm,
    exclude=[
        'created_at',
        'currency',
        'hash',
        'updated_at',
        'user',
    ],
    converter=model_converter
)


CashupForm = model_form(
    Cashup,
    db.session,
    FlaskForm,
    exclude=[
        'adjustments',
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
        'vat_rates',
    ],
    exclude_pk=False,
    field_args={
        'id': {
            'label': 'ID',
        },
    }
)


CurrencyForm = model_form(
    Currency,
    db.session,
    FlaskForm,
    exclude=[
        'adjustments',
        'created_at',
        'networks',
        'orders',
        'products',
        'transactions',
        'updated_at',
    ],
    exclude_pk=False,
    field_args={
        'id': {
            'label': 'ID',
        },
    }
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
        'adjustments',
        'auths',
        'cashups',
        'created_at',
        'categories',
        'last_ping_ip',
        'last_ping_at',
        'last_ping_user_agent',
        'last_ping_sys_uptime',
        'last_ping_wifidog_uptime',
        'last_ping_sys_memfree',
        'last_ping_sys_load',
        'orders',
        'products',
        'transactions',
        'updated_at',
        'users',
        'vouchers',
    ],
    exclude_pk=False,
    field_args={
        'id': {
            'label': 'ID',
        },
        'gateway_type': {
            'default': lambda: GatewayType.query.get('cafe'),
        },
        'logo': {
            'description': 'Images only, resampled down to 300 x 300 pixels.',
        },
        'network': {
            'default': lambda: current_user.network,
            'query_factory': instances('network'),
        },
        'url_facebook': {
            'label': 'Facebook Page',
        },
        'url_home': {
            'label': 'Home Page',
        },
        'url_map': {
            'label': 'Map URL',
        },
        'vat_number': {
            'label': 'VAT Number',
        },
    },
    converter=GatewayConverter()
)

NetworkForm = model_form(
    Network,
    db.session,
    FlaskForm,
    exclude=[
        'adjustments',
        'categories',
        'created_at',
        'gateways',
        'orders',
        'products',
        'transactions',
        'updated_at',
        'users',
    ],
    exclude_pk=False,
    field_args={
        'ga_tracking_id': {
            'label': 'Google Analytics Tracking ID',
        },
        'id': {
            'label': 'ID',
        },
    }
)


ProductForm = model_form(
    Product,
    db.session,
    FlaskForm,
    exclude=[
        'created_at',
        'gateway',
        'network',
        'order_items',
        'updated_at',
    ],
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
    category = QuerySelectField('Category', query_factory=instances('category'))


class SelectNetworkGatewayForm(FlaskForm):
    network = QuerySelectField('Network', default=lambda: current_user.network, query_factory=instances('network'))
    gateway = QuerySelectField('Gateway', allow_blank=True, default=lambda: current_user.gateway, query_factory=instances('gateway'))


class FilterForm(FlaskForm):
    def filter_query(self, query):
        for k, v in self.data.items():
            if v:
                if hasattr(self, 'filter_%s' % k):
                    query = getattr(self, 'filter_%s' % k)(query, k, v)
                else:
                    query = query.filter_by(**{k: v})
        return query


class TransactionFilterForm(FilterForm):
    network = QuerySelectField('Network', allow_blank=True, query_factory=instances('network'), blank_text='Select Network')
    gateway = QuerySelectField('Gateway', allow_blank=True, query_factory=instances('gateway'), blank_text='Select Gateway')
    user = QuerySelectField('User', allow_blank=True, query_factory=instances('user'), blank_text='Select User')
    status = f.SelectField('Status', default='', choices=[('', 'Select Status')] + [(status, status) for status in graphs['order']['states'].keys()])
    created_from = f.TextField('Created From')
    created_to = f.TextField('Created To')

    def filter_created_from(self, q, k, v):
        return q.filter(Transaction.created_at >= v)

    def filter_created_to(self, q, k, v):
        return q.filter(Transaction.created_at < v)


class UserFilterForm(FilterForm):
    network = QuerySelectField('Network', allow_blank=True, query_factory=instances('network'), blank_text='Select Network')
    gateway = QuerySelectField('Gateway', allow_blank=True, query_factory=instances('gateway'), blank_text='Select Gateway')
    email = f.TextField('Email')

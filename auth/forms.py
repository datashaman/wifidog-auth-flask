from __future__ import absolute_import

from auth.graphs import graphs
from auth.models import db, Adjustment, Cashup, Country, Currency, Product, Transaction
from auth.resources import resource_query
from flask_security import current_user
from flask_wtf import FlaskForm
from wtforms import fields as f, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.ext.sqlalchemy.orm import converts, model_form, ModelConverter as BaseModelConverter


def instances(resource):
    def func():
        return resource_query(resource).all()
    return func


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


class BroadcastForm(FlaskForm):
    message = f.StringField('Message', [validators.InputRequired()])


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
    created_from = f.StringField('Created From')
    created_to = f.StringField('Created To')

    def filter_created_from(self, q, k, v):
        return q.filter(Transaction.created_at >= v)

    def filter_created_to(self, q, k, v):
        return q.filter(Transaction.created_at < v)

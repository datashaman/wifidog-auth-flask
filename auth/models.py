from __future__ import absolute_import
from __future__ import division

import datetime
import simplejson as json
import sqlalchemy.types as types

from auth.graphs import graphs
from auth.services import db
from auth.utils import render_currency_amount, generate_code, generate_order_hash, generate_uuid
from decimal import Decimal
from flask import current_app
from flask_security import UserMixin, RoleMixin, current_user, SQLAlchemyUserDatastore
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import backref
from sqlalchemy.schema import UniqueConstraint


class SqliteDecimal(types.TypeDecorator):
    impl = types.INTEGER

    def process_bind_param(self, value, dialect):
        return None if value is None else int(value * 100)

    def process_result_value(self, value, dialect):
        return None if value is None else Decimal(value / 100)


def available_actions(graph, status, interface):
    result = {}
    for action, defn in graph['actions'].items():
        if status is None or (action in graph['states'][status] and defn['interface'] == interface):
            result[action] = defn
    return result


@event.listens_for(Engine, 'connect')
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON;')
    cursor.close()


@event.listens_for(Engine, 'close')
def optimize_on_close(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA optimize;')
    cursor.close()


roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('roles.id'))
)

current_timestamp = datetime.datetime.utcnow


class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.Unicode(20), unique=True)
    description = db.Column(db.Unicode(40))

    def __str__(self):
        return self.description


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    network_id = db.Column(db.Unicode(20), db.ForeignKey('networks.id', ondelete='cascade', onupdate='cascade'))
    network = db.relationship('Network', backref=backref('users', lazy='dynamic'))

    gateway_id = db.Column(db.Unicode(20), db.ForeignKey('gateways.id', ondelete='cascade', onupdate='cascade'))
    gateway = db.relationship('Gateway', backref=backref('users', lazy='dynamic'))

    first_name = db.Column(db.Unicode(40))
    last_name = db.Column(db.Unicode(40))

    email = db.Column(db.Unicode(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    mobile = db.Column(db.String(20))

    active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=current_timestamp)
    confirmed_at = db.Column(db.DateTime())

    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    locale = db.Column(db.String)
    timezone = db.Column(db.String)

    __table_args__ = (
        UniqueConstraint('network_id', 'email'),
    )

    def __str__(self):
        return self.email


users = SQLAlchemyUserDatastore(db, User, Role)


country_currencies = db.Table('country_currencies',
    db.Column('country_id', db.String(3), db.ForeignKey('countries.id')),
    db.Column('currency_id', db.String(3), db.ForeignKey('currencies.id'))
)

country_processors = db.Table('country_processors',
    db.Column('country_id', db.String(3), db.ForeignKey('countries.id')),
    db.Column('processor_id', db.String(20), db.ForeignKey('processors.id'))
)

class Country(db.Model):
    __tablename__ = 'countries'

    id = db.Column(db.String(3), primary_key=True)
    title = db.Column(db.Unicode(40), unique=True, nullable=False)

    currencies = db.relationship('Currency', secondary=country_currencies,
            backref=db.backref('countries', lazy='dynamic'))

    processors = db.relationship('Processor', secondary=country_processors,
            backref=db.backref('countries', lazy='dynamic'))

    def __str__(self):
        return self.title

class Currency(db.Model):
    __tablename__ = 'currencies'

    id = db.Column(db.String(3), primary_key=True)
    title = db.Column(db.Unicode(20), unique=True, nullable=False)
    prefix = db.Column(db.String(10))
    suffix = db.Column(db.String(10))

    def __str__(self):
        return self.title

class Network(db.Model):
    __tablename__ = 'networks'

    id = db.Column(db.Unicode(20), primary_key=True)

    title = db.Column(db.Unicode(40), nullable=False)
    description = db.Column(db.UnicodeText)
    ga_tracking_id = db.Column(db.String(20))

    currency_id = db.Column(db.String(3), db.ForeignKey('currencies.id', onupdate='cascade'), nullable=False)
    currency = db.relationship(Currency, backref=backref('networks', lazy='dynamic'))

    created_at = db.Column(db.DateTime, default=current_timestamp)

    def __str__(self):
        return self.title


class GatewayType(db.Model):
    __tablename__ = 'gateway_types'

    id = db.Column(db.String(20), primary_key=True)
    title = db.Column(db.Unicode(255), unique=True, nullable=False)

    def __str__(self):
        return self.title


class Gateway(db.Model):
    __tablename__ = 'gateways'

    id = db.Column(db.Unicode(20), primary_key=True)

    network_id = db.Column(db.Unicode(20), db.ForeignKey('networks.id', ondelete='cascade', onupdate='cascade'), nullable=False)
    network = db.relationship(Network, backref=backref('gateways', lazy='dynamic'))

    title = db.Column(db.Unicode(40), nullable=False)
    subtitle = db.Column(db.Unicode(60))
    description = db.Column(db.UnicodeText)

    status = db.Column(db.String(20), default='new')

    gateway_type_id = db.Column(db.Unicode(20), db.ForeignKey('gateway_types.id', onupdate='cascade'), nullable=False)
    gateway_type = db.relationship(GatewayType, backref=backref('gateways', lazy='dynamic'))

    contact_email = db.Column(db.Unicode(255))
    contact_phone = db.Column(db.String)

    public_email = db.Column(db.Unicode(255))
    public_phone = db.Column(db.String)

    url_home = db.Column(db.Unicode(255))
    url_facebook = db.Column(db.Unicode(255))

    url_map = db.Column(db.Unicode(255))

    logo = db.Column(db.Unicode(255))

    login_ask_name = db.Column(db.Boolean(), default=False)
    login_require_name = db.Column(db.Boolean(), default=False)

    default_minutes = db.Column(db.Integer)
    default_megabytes = db.Column(db.BigInteger)

    support_email = db.Column(db.Unicode(255))

    vat_number = db.Column(db.String(20))

    business_name = db.Column(db.Unicode(40))
    business_address = db.Column(db.Unicode(255))

    country_id = db.Column(db.String(3), db.ForeignKey('countries.id', onupdate='cascade'), nullable=False, default=lambda: current_app.config['DEFAULT_COUNTRY'])
    country = db.relationship('Country', backref=backref('gateways', lazy='dynamic'))

    last_ping_ip = db.Column(db.String(15))
    last_ping_at = db.Column(db.DateTime)
    last_ping_user_agent = db.Column(db.Unicode(255))
    last_ping_sys_uptime = db.Column(db.Integer)
    last_ping_wifidog_uptime = db.Column(db.Integer)
    last_ping_sys_memfree = db.Column(db.Integer)
    last_ping_sys_load = db.Column(db.Integer)

    created_at = db.Column(db.DateTime, default=current_timestamp)

    def __str__(self):
        return self.title

def record_change(f):
    def func(self, **kwargs):
        source_status = self.status

        f(self)

        change = Change()
        change.changed_type = type(self).__name__
        change.changed_id = self.id
        change.event = f.__name__
        change.source = source_status
        change.destination = self.status
        change.args = json.dumps(kwargs)

        if current_user.is_authenticated:
            change.user_id = getattr(current_user, 'id', None)

        db.session.add(change)

    return func

class Voucher(db.Model):
    __tablename__ = 'vouchers'

    id = db.Column(db.Integer, primary_key=True)

    minutes = db.Column(db.Integer, nullable=False)
    megabytes = db.Column(db.BigInteger)
    created_at = db.Column(db.DateTime, default=current_timestamp)
    updated_at = db.Column(db.DateTime, default=current_timestamp, onupdate=current_timestamp)
    started_at = db.Column(db.DateTime)
    gw_address = db.Column(db.String(15))
    gw_port = db.Column(db.String(5))

    gateway_id = db.Column(db.Unicode(20), db.ForeignKey('gateways.id', ondelete='cascade',  onupdate='cascade'), nullable=False)
    gateway = db.relationship(Gateway, backref=backref('vouchers', lazy='dynamic'))

    order_id = db.Column(db.Unicode(20), db.ForeignKey('orders.id', ondelete='cascade',  onupdate='cascade'))
    order = db.relationship('Order', backref=backref('vouchers', lazy='dynamic'))

    code = db.Column(db.String(20), default=generate_code, nullable=False)

    mac = db.Column(db.String(20))
    ip = db.Column(db.String(15))
    url = db.Column(db.Unicode(255))
    name = db.Column(db.Unicode(255))
    email = db.Column(db.Unicode(255))
    token = db.Column(db.String(255))
    incoming = db.Column(db.BigInteger, default=0)
    outgoing = db.Column(db.BigInteger, default=0)

    status = db.Column(db.String(20), nullable=False, default='new')

    __table_args__ = (
            UniqueConstraint('gateway_id', 'code'),
    )

    def should_expire(self):
        return self.expires_at < datetime.datetime.utcnow()

    def should_end(self):
        return self.started_at is not None and self.end_at < datetime.datetime.utcnow()

    def megabytes_are_finished(self):
        return self.megabytes is not None and (self.incoming + self.outgoing) / (1024 * 1024) >= self.megabytes

    @property
    def time_left(self):
        if self.started_at:
            if self.should_end():
                return 0
            else:
                seconds = (self.end_at - datetime.datetime.utcnow()).seconds
                seconds = max(0, seconds)
                return int(seconds / 60)

    @property
    def end_at(self):
        if self.started_at:
            return self.started_at + datetime.timedelta(minutes=self.minutes)

    @property
    def expires_at(self):
        return self.created_at + datetime.timedelta(minutes=current_app.config.get('VOUCHER_MAXAGE'))

    @record_change
    def extend(self):
        self.minutes += 30

    @record_change
    def login(self):
        self.started_at = datetime.datetime.utcnow()
        self.status = 'active'

    @record_change
    def end(self):
        self.status = 'ended'

    @record_change
    def expire(self):
        self.status = 'expired'

    @record_change
    def block(self):
        self.status = 'blocked'

    @record_change
    def unblock(self):
        self.status = 'active'

    @record_change
    def archive(self):
        self.status = 'archived'

    @property
    def available_actions(self):
        return available_actions(graphs['voucher'], self.status, 'admin')

    @property
    def class_hint(self):
        choices = {
            'new': 'success',
            'active': 'active',
            'expired': 'info',
            'ended': 'info',
            'blocked': 'warning',
        }
        return choices.get(self.status, 'default')

    def __str__(self):
        return self.code


class Change(db.Model):
    __tablename__ = 'changes'

    id = db.Column(db.Integer, primary_key=True)
    changed_type = db.Column(db.String(40))
    changed_id = db.Column(db.Integer)
    event = db.Column(db.String(20))
    source = db.Column(db.String(20))
    destination = db.Column(db.String(20))
    args = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade', onupdate='cascade'))
    user = db.relationship(User, backref=backref('changes', lazy='dynamic'))
    created_at = db.Column(db.DateTime, default=current_timestamp)


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)

    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='cascade', onupdate='cascade'), nullable=True)
    children = db.relationship('Category', backref=backref('sub_categories', remote_side=[id]))

    network_id = db.Column(db.Unicode(20), db.ForeignKey('networks.id', ondelete='cascade', onupdate='cascade'))
    network = db.relationship(Network, backref=backref('categories', lazy='dynamic'))

    gateway_id = db.Column(db.Unicode(20), db.ForeignKey('gateways.id', ondelete='cascade', onupdate='cascade'))
    gateway = db.relationship(Gateway, backref=backref('categories', lazy='dynamic'))

    code = db.Column(db.Unicode(10), nullable=False)
    title = db.Column(db.Unicode(40), nullable=False)

    description = db.Column(db.UnicodeText)

    read_only = db.Column(db.Boolean, nullable=False, default=False)
    properties = db.Column(db.UnicodeText)

    sequence = db.Column(db.Integer)

    created_at = db.Column(db.DateTime, default=current_timestamp)
    updated_at = db.Column(db.DateTime, default=current_timestamp, onupdate=current_timestamp)

    __table_args__ = (
            UniqueConstraint('network_id', 'gateway_id', 'parent_id', 'code'),
            UniqueConstraint('network_id', 'gateway_id', 'parent_id', 'title'),
    )

    def __str__(self):
        return self.title

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)

    network_id = db.Column(db.Unicode(20), db.ForeignKey('networks.id', ondelete='cascade', onupdate='cascade'), nullable=False)
    network = db.relationship(Network, backref=backref('products', lazy='dynamic'))

    gateway_id = db.Column(db.Unicode(20), db.ForeignKey('gateways.id', ondelete='cascade', onupdate='cascade'))
    gateway = db.relationship(Gateway, backref=backref('products', lazy='dynamic'))

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', onupdate='cascade'), nullable=False)
    category = db.relationship(Category, backref=backref('products', lazy='dynamic'))

    code = db.Column(db.Unicode(10), nullable=False)
    title = db.Column(db.Unicode(40), nullable=False)
    unit = db.Column(db.String(20))
    description = db.Column(db.UnicodeText)

    price = db.Column(SqliteDecimal, nullable=False)

    properties = db.Column(db.UnicodeText)

    sequence = db.Column(db.Integer)

    vat_rate_id = db.Column(db.String(20), db.ForeignKey('vat_rates.id', onupdate='cascade'), nullable=False)
    vat_rate = db.relationship('VatRate', backref=backref('products', lazy='dynamic'))

    created_at = db.Column(db.DateTime, default=current_timestamp)
    updated_at = db.Column(db.DateTime, default=current_timestamp, onupdate=current_timestamp)

    __table_args__ = (
            UniqueConstraint('network_id', 'gateway_id', 'code'),
            UniqueConstraint('network_id', 'gateway_id', 'title', 'unit'),
    )

    def __str__(self):
        return '%s %s%s' % (self.title,
                            render_currency_amount(self.network.currency,
                                                   self.price),
                            ' %s' % self.unit if self.unit else '')

    def __getattr__(self, name):
        if 'properties' in self.__dict__ and self.__dict__['properties']:
            for line in self.__dict__['properties'].split('\n'):
                (k, v) = line.split('=')
                if k == name:
                    return v
        return super(db.Model, self).__getattr__(name)


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.String(40), unique=True, nullable=False, default=generate_order_hash)

    gateway_id = db.Column(db.Unicode(20), db.ForeignKey('gateways.id', ondelete='cascade', onupdate='cascade'), nullable=False)
    gateway = db.relationship(Gateway, backref=backref('orders', lazy='dynamic'))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='set null', onupdate='cascade'), nullable=False)
    user = db.relationship(User, backref=backref('orders', lazy='dynamic'))

    status = db.Column(db.String(20), nullable=False, default='new')

    currency_id = db.Column(db.String(3), db.ForeignKey('currencies.id', ondelete='cascade', onupdate='cascade'), nullable=False)
    currency = db.relationship(Currency, backref=backref('orders', lazy='dynamic'))

    vat_amount = db.Column(SqliteDecimal, nullable=False)
    total_amount = db.Column(SqliteDecimal, nullable=False)

    created_at = db.Column(db.DateTime, default=current_timestamp)
    updated_at = db.Column(db.DateTime, default=current_timestamp, onupdate=current_timestamp)

    @record_change
    def cancel(self):
        self.status = 'cancelled'

    @record_change
    def uncancel(self):
        self.status = 'new'

    @record_change
    def archive(self):
        self.status = 'archived'

    @property
    def available_actions(self):
        return available_actions(graphs['order'], self.status, 'admin')

    @property
    def paid_transactions(self):
        return self.transactions.filter_by(status='successful', type='payment')

    @property
    def paid_amount(self):
        return Decimal(sum(t.total_amount for t in self.paid_transactions))

    @property
    def owed_amount(self):
        return Decimal(max(self.total_amount - self.paid_amount, Decimal(0)))

    @property
    def network(self):
        return self.gateway.network

    @property
    def class_hint(self):
        choices = {
            'new': 'active',
            'paid': 'success',
        }
        return choices.get(self.status, 'default')

    def calculate_totals(self):
        self.total_amount = Decimal(0)
        self.vat_amount = Decimal(0)
        for item in self.items:
            self.total_amount += item.total_amount
            self.vat_amount += item.vat_amount

    def __str__(self):
        return 'Order #%08d' % self.id


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='cascade', onupdate='cascade'), nullable=False)
    order = db.relationship(Order, backref=backref('items', lazy='dynamic'))

    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='cascade', onupdate='cascade'), nullable=False)
    product = db.relationship(Product, backref=backref('order_items', lazy='dynamic'))

    description = db.Column(db.Unicode(40))

    quantity = db.Column(SqliteDecimal, default=1, nullable=False)
    price = db.Column(SqliteDecimal, nullable=False)

    created_at = db.Column(db.DateTime, default=current_timestamp)
    updated_at = db.Column(db.DateTime, default=current_timestamp, onupdate=current_timestamp)

    @property
    def total_amount(self):
        return self.quantity * self.price

    @property
    def vat_amount(self):
        percentage = self.product.vat_rate.percentage
        return self.total_amount * percentage / (Decimal(100) + percentage)

    def __str__(self):
        return '%d x %s' % (self.quantity, self.product)

    @property
    def available_actions(self):
        return available_actions(graphs['order_item'], None, 'admin')


class Processor(db.Model):
    __tablename__ = 'processors'

    id = db.Column(db.Unicode(20), primary_key=True)
    title = db.Column(db.Unicode(40))
    active = db.Column(db.Boolean, nullable=False, default=True)
    international = db.Column(db.Boolean, nullable=False, default=False)

    def pay_order(self, order):
        from auth.processors import get_processor
        return get_processor(self.id).pay_order(order)

    def __str__(self):
        return self.title


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.String(40), default=generate_uuid, nullable=False, unique=True)

    status = db.Column(db.String(20), nullable=False, default='new')

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade', onupdate='cascade'))
    user = db.relationship(User, backref=backref('transactions', lazy='dynamic'))

    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='cascade', onupdate='cascade'), nullable=False)
    order = db.relationship(Order, backref=backref('transactions', lazy='dynamic'))

    type = db.Column(db.String(20), nullable=False, default='payment')

    processor_id = db.Column(db.Integer, db.ForeignKey('processors.id', ondelete='cascade', onupdate='cascade'), nullable=False)
    processor = db.relationship(Processor, backref=backref('transactions', lazy='dynamic'))

    processor_reference = db.Column(db.String(40))

    currency_id = db.Column(db.String(3), db.ForeignKey('currencies.id', ondelete='cascade', onupdate='cascade'), nullable=False)
    currency = db.relationship(Currency, backref=backref('transactions', lazy='dynamic'))

    total_amount = db.Column(SqliteDecimal, nullable=False)
    tip_amount = db.Column(SqliteDecimal)

    payload = db.Column(db.UnicodeText)

    cashup_id = db.Column(db.String(40), db.ForeignKey('cashups.id', ondelete='cascade', onupdate='cascade'))
    cashup = db.relationship('Cashup', backref=backref('transactions', lazy='dynamic'))

    created_at = db.Column(db.DateTime, default=current_timestamp)
    updated_at = db.Column(db.DateTime, default=current_timestamp, onupdate=current_timestamp)

    __table_args__ = (
        UniqueConstraint('processor_id', 'processor_reference'),
    )

    @record_change
    def archive(self):
        self.status = 'archived'

    @property
    def available_actions(self):
        return available_actions(graphs['transaction'], self.status, 'admin')

    @property
    def class_hint(self):
        if self.cashup:
            return 'info'

        choices = {
            'new': 'active',
            'failed': 'danger',
            'successful': 'success',
        }
        return choices.get(self.status, 'default')

    @property
    def network(self):
        return self.order.network

    @property
    def gateway(self):
        return self.order.gateway

    def __str__(self):
        return 'Transaction #%08d' % self.id


class Cashup(db.Model):
    __tablename__ = 'cashups'

    id = db.Column(db.String(40), primary_key=True, default=generate_uuid)

    gateway_id = db.Column(db.Unicode(20), db.ForeignKey('gateways.id', ondelete='cascade', onupdate='cascade'), nullable=False)
    gateway = db.relationship(Gateway, backref=backref('cashups', lazy='dynamic'))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade', onupdate='cascade'), nullable=False)
    user = db.relationship(User, backref=backref('cashups', lazy='dynamic'))

    created_at = db.Column(db.DateTime, default=current_timestamp)

    def __str__(self):
        return self.id


class VatRate(db.Model):
    __tablename__ = 'vat_rates'

    id = db.Column(db.String(20), primary_key=True)
    title = db.Column(db.String(20), nullable=False, unique=True)

    country_id = db.Column(db.String(3), db.ForeignKey('countries.id', onupdate='cascade'), nullable=False, default=lambda: current_app.config['DEFAULT_COUNTRY'])
    country = db.relationship('Country', backref=backref('vat_rates', lazy='dynamic'))

    percentage = db.Column(SqliteDecimal, nullable=False)

    def __str__(self):
        return '%.2f%%' % self.percentage


class Adjustment(db.Model):
    __tablename__ = 'adjustments'

    id = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.UnicodeText, nullable=False)

    network_id = db.Column(db.Unicode(20), db.ForeignKey('networks.id', ondelete='cascade', onupdate='cascade'), nullable=False)
    network = db.relationship(Network, backref=backref('adjustments', lazy='dynamic'))

    gateway_id = db.Column(db.Unicode(20), db.ForeignKey('gateways.id', ondelete='cascade', onupdate='cascade'), nullable=False)
    gateway = db.relationship(Gateway, backref=backref('adjustments', lazy='dynamic'))

    amount = db.Column(SqliteDecimal, nullable=False)

    created_at = db.Column(db.DateTime, default=current_timestamp)
    updated_at = db.Column(db.DateTime, default=current_timestamp, onupdate=current_timestamp)

    @property
    def available_actions(self):
        return available_actions(graphs['adjustment'], None, 'admin')

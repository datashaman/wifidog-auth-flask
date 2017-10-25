import base64
import datetime
import json
import re
import string
import uuid

import flask

from app.graphs import states, available_actions
from flask import current_app
from flask_potion import fields
from flask_security import UserMixin, RoleMixin, current_user, SQLAlchemyUserDatastore, Security
from flask_sqlalchemy import SQLAlchemy
from random import choice

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import backref
from sqlalchemy.schema import PrimaryKeyConstraint, UniqueConstraint

import constants

@event.listens_for(Engine, 'connect')
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.close()

db = SQLAlchemy()

chars = string.letters + string.digits

def generate_token():
    return uuid.uuid4().hex

def generate_id():
    source = ''.join(choice(chars) for _ in range(4))
    encoded = base64.b32encode(source)
    result = unicode(re.sub(r'=*$', '', encoded))
    return result

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('roles.id'))
)

class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.Unicode(20), unique=True)
    description = db.Column(db.Unicode(40))

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    network_id = db.Column(db.Unicode(20), db.ForeignKey('networks.id', onupdate='cascade'))
    network = db.relationship('Network', backref=backref('users', lazy='dynamic'))

    gateway_id = db.Column(db.Unicode(20), db.ForeignKey('gateways.id', onupdate='cascade'))
    gateway = db.relationship('Gateway', backref=backref('users', lazy='dynamic'))

    email = db.Column(db.Unicode(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    __table_args__ = (
        UniqueConstraint('network_id', 'email'),
    )

users = SQLAlchemyUserDatastore(db, User, Role)

class Network(db.Model):
    __tablename__ = 'networks'

    id = db.Column(db.Unicode(20), primary_key=True)

    title = db.Column(db.Unicode(40), nullable=False)
    description = db.Column(db.UnicodeText)
    ga_tracking_id = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

class Gateway(db.Model):
    __tablename__ = 'gateways'

    id = db.Column(db.Unicode(20), primary_key=True)

    network_id = db.Column(db.Unicode(20), db.ForeignKey('networks.id', onupdate='cascade'), nullable=False)
    network = db.relationship(Network, backref=backref('gateways', lazy='dynamic'))

    title = db.Column(db.Unicode(40), nullable=False)
    subtitle = db.Column(db.Unicode(60))
    description = db.Column(db.UnicodeText)

    contact_email = db.Column(db.Unicode(255))
    contact_phone = db.Column(db.String)

    url_home = db.Column(db.Unicode(255))
    url_facebook = db.Column(db.Unicode(255))

    logo = db.Column(db.String(255))

    login_ask_name = db.Column(db.Boolean(), default=False)
    login_require_name = db.Column(db.Boolean(), default=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

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
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    started_at = db.Column(db.DateTime)
    gw_address = db.Column(db.String(15))
    gw_port = db.Column(db.String(5))

    gateway_id = db.Column(db.Unicode(20), db.ForeignKey('gateways.id', onupdate='cascade'), nullable=False)
    gateway = db.relationship(Gateway, backref=backref('vouchers', lazy='dynamic'))

    code = db.Column(db.String(20), default=generate_id, nullable=False)

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
        return self.created_at + datetime.timedelta(minutes=current_app.config.get('VOUCHER_MAXAGE')) < datetime.datetime.utcnow()

    def should_end(self):
        if self.started_at:
            return self.started_at + datetime.timedelta(minutes=self.minutes) < datetime.datetime.utcnow()
        else:
            return False

    @property
    def time_left(self):
        if self.started_at:
            if self.should_end():
                return 0
            else:
                seconds = ((self.started_at + datetime.timedelta(minutes=self.minutes)) - datetime.datetime.utcnow()).seconds
                seconds = max(0, seconds)
                return seconds / 60

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
        return available_actions(self.status, 'admin')

class Auth(db.Model):
    __tablename__ = 'auths'

    id = db.Column(db.Integer, primary_key=True)
    user_agent = db.Column(db.String(255))
    stage = db.Column(db.String(20))
    ip = db.Column(db.String(20))
    mac = db.Column(db.String(20))
    token = db.Column(db.String(255))
    incoming = db.Column(db.BigInteger)
    outgoing = db.Column(db.BigInteger)

    gateway_id = db.Column(db.Unicode(20), db.ForeignKey('gateways.id', onupdate='cascade'), nullable=False)
    gateway = db.relationship(Gateway, backref=backref('auths', lazy='dynamic'))

    voucher_id = db.Column(db.Integer, db.ForeignKey('vouchers.id', onupdate='cascade'))
    voucher = db.relationship(Voucher, backref=backref('auths', lazy='dynamic'))

    status = db.Column(db.Integer)
    messages = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def matches_voucher(self, voucher):
        return self.gateway_id == voucher.gateway_id and self.mac == voucher.mac and self.ip == voucher.ip

    def process_request(self):
        if self.token is None:
            return (constants.AUTH_DENIED, 'No connection token provided')

        voucher = Voucher.query.filter_by(token=self.token).first()

        if voucher is None:
            return (constants.AUTH_DENIED, 'Requested token not found: %s' % self.token)
        else:
            self.voucher_id = voucher.id

        if voucher.ip is None:
            voucher.ip = flask.request.args.get('ip')

        if voucher.status in [ 'ended', 'expired' ]:
            return (constants.AUTH_DENIED, 'Requested token is the wrong status: %s' % self.token)

        if self.stage == constants.STAGE_LOGIN:
            if voucher.started_at is None:
                if voucher.should_expire():
                    voucher.expire()
                    return (constants.AUTH_DENIED, 'Token has expired: %s' % self.token)

                voucher.login()
                return (constants.AUTH_ALLOWED, None)
            else:
                if self.matches_voucher(voucher):
                    if voucher.should_end():
                        voucher.end()
                        return (constants.AUTH_DENIED, 'Token is in use but has ended: %s' % self.token)
                    else:
                        return (constants.AUTH_ALLOWED, 'Token is already in use but details match: %s' % self.token)
                else:
                    return (constants.AUTH_DENIED, 'Token is already in use: %s' % self.token)
        elif self.stage in [ constants.STAGE_LOGOUT, constants.STAGE_COUNTERS ]:
            messages = ''

            if self.incoming is not None or self.outgoing is not None:
                if self.incoming > voucher.incoming:
                    voucher.incoming = self.incoming
                else:
                    messages += '| Warning: Incoming counter is smaller than stored value; counter not updated'

                if self.outgoing > voucher.outgoing:
                    voucher.outgoing = self.outgoing
                else:
                    messages += '| Warning: Outgoing counter is smaller than stored value; counter not updated'
            else:
                messages += '| Incoming or outgoing counter is missing; counters not updated'

            if self.stage == constants.STAGE_LOGOUT:
                # Ignore this, when you login the timer starts, that's it
                # (at least it is for this model)
                messages += '| Logout is not implemented'

            if voucher.started_at is not None and voucher.should_end():
                voucher.end()
                return (constants.AUTH_DENIED, 'Token has ended: %s' % self.token)

            return (constants.AUTH_ALLOWED, messages)
        else:
            return (constants.AUTH_ERROR, 'Unknown stage: %s' % self.stage)

class Ping(db.Model):
    __tablename__ = 'pings'

    id = db.Column(db.Integer, primary_key=True)
    user_agent = db.Column(db.String(255))

    gateway_id = db.Column(db.Unicode(20), db.ForeignKey('gateways.id', onupdate='cascade'), nullable=False)
    gateway = db.relationship(Gateway, backref=backref('pings', lazy='dynamic'))

    sys_uptime = db.Column(db.BigInteger)
    sys_memfree = db.Column(db.BigInteger)
    sys_load = db.Column(db.String)
    wifidog_uptime = db.Column(db.BigInteger)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

class Change(db.Model):
    __tablename__ = 'changes'

    id = db.Column(db.Integer, primary_key=True)
    changed_type = db.Column(db.String(40))
    changed_id = db.Column(db.Integer)
    event = db.Column(db.String(20))
    source = db.Column(db.String(20))
    destination = db.Column(db.String(20))
    args = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship(User, backref=backref('changes', lazy='dynamic'))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

country_currencies = db.Table('country_currencies',
    db.Column('country_id', db.String(3), db.ForeignKey('countries.id')),
    db.Column('currency_id', db.String(3), db.ForeignKey('currencies.id'))
)

class Country(db.Model):
    __tablename__ = 'countries'

    id = db.Column(db.String(3), primary_key=True)
    title = db.Column(db.Unicode(40), unique=True, nullable=False)

    currencies = db.relationship('Currency', secondary=country_currencies,
            backref=db.backref('countries', lazy='dynamic'))

class Currency(db.Model):
    __tablename__ = 'currencies'

    id = db.Column(db.String(3), primary_key=True)
    title = db.Column(db.Unicode(20), unique=True, nullable=False)
    prefix = db.Column(db.String(10))
    suffix = db.Column(db.String(10))

product_categories = db.Table('product_categories',
    db.Column('product_id', db.Integer, db.ForeignKey('products.id')),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id')),
)

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)

    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id', onupdate='cascade'), nullable=True)
    children = db.relationship('Category', backref=backref('sub_categories', remote_side=[id]))

    network_id = db.Column(db.Unicode(20), db.ForeignKey('networks.id', onupdate='cascade'), nullable=False)
    network = db.relationship(Network, backref=backref('categories', lazy='dynamic'))

    gateway_id = db.Column(db.Unicode(20), db.ForeignKey('gateways.id', onupdate='cascade'))
    gateway = db.relationship(Gateway, backref=backref('categories', lazy='dynamic'))

    code = db.Column(db.Unicode(10), nullable=False)
    title = db.Column(db.Unicode(40), nullable=False)

    description = db.Column(db.UnicodeText)

    status = db.Column(db.String(20), nullable=False, default='new')

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)

    __table_args__ = (
            UniqueConstraint('network_id', 'gateway_id', 'parent_id', 'code'),
            UniqueConstraint('network_id', 'gateway_id', 'parent_id', 'title'),
    )

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)

    network_id = db.Column(db.Unicode(20), db.ForeignKey('networks.id', onupdate='cascade'), nullable=False)
    network = db.relationship(Network, backref=backref('products', lazy='dynamic'))

    gateway_id = db.Column(db.Unicode(20), db.ForeignKey('gateways.id', onupdate='cascade'))
    gateway = db.relationship(Gateway, backref=backref('products', lazy='dynamic'))

    categories = db.relationship(Category, secondary=product_categories, backref=db.backref('products', lazy='dynamic'))

    code = db.Column(db.Unicode(10), nullable=False)
    title = db.Column(db.Unicode(40), nullable=False)

    description = db.Column(db.UnicodeText)

    currency_id = db.Column(db.String(3), db.ForeignKey('currencies.id', onupdate='cascade'))
    currency = db.relationship(Currency, backref=backref('products', lazy='dynamic'))

    price = db.Column(db.Integer) # Cents

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)

    __table_args__ = (
            UniqueConstraint('network_id', 'gateway_id', 'code'),
            UniqueConstraint('network_id', 'gateway_id', 'title'),
    )

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship(User, backref=backref('orders', lazy='dynamic'))

    network_id = db.Column(db.Unicode(20), db.ForeignKey('networks.id', onupdate='cascade'), nullable=False)
    network = db.relationship(Network, backref=backref('orders', lazy='dynamic'))

    gateway_id = db.Column(db.Unicode(20), db.ForeignKey('gateways.id', onupdate='cascade'))
    gateway = db.relationship(Gateway, backref=backref('orders', lazy='dynamic'))

    status = db.Column(db.String(20), nullable=False, default='new')

    currency_id = db.Column(db.String(3), db.ForeignKey('currencies.id', onupdate='cascade'), nullable=False)
    currency = db.relationship(Currency, backref=backref('orders', lazy='dynamic'))

    price = db.Column(db.Integer, nullable=False) # Cents

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)

    product_id = db.Column(db.Integer, db.ForeignKey('products.id', onupdate='cascade'), nullable=False)
    product = db.relationship(Product, backref=backref('order_items', lazy='dynamic'))

    description = db.Column(db.Unicode(40))

    units = db.Column(db.Integer, default=1, nullable=False)

    price_per_unit = db.Column(db.Integer, nullable=False) # Cents
    price = db.Column(db.Integer, nullable=False) # Cents

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.String(40), primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship(User, backref=backref('transactions', lazy='dynamic'))

    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', onupdate='cascade'))
    order = db.relationship(Order, backref=backref('transactions', lazy='dynamic'))

    type = db.Column(db.String(20), nullable=False, default='payment')

    payload = db.Column(db.UnicodeText)

    status = db.Column(db.String(20), nullable=False, default='new')
    reference = db.Column(db.String(40))

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

import base64
import datetime
import re
import string
import uuid

from app.services import db, api, principals
from flask.ext.potion import fields
from flask.ext.security import UserMixin, RoleMixin, current_user
from random import choice
from sqlalchemy.orm import backref

import constants


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

    name = db.Column(db.Unicode(80), unique=True)
    description = db.Column(db.Unicode(255))

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    network_id = db.Column(db.Unicode, db.ForeignKey('networks.id'))
    network = db.relationship('Network', backref=backref('users', lazy='dynamic'))

    gateway_id = db.Column(db.Unicode, db.ForeignKey('gateways.id'))
    gateway = db.relationship('Gateway', backref=backref('users', lazy='dynamic'))

    email = db.Column(db.Unicode(255), unique=True, nullable=False)
    password = db.Column(db.Unicode(255), nullable=False)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return '<User %r>' % self.email

    def to_dict(self):
        return { c.name: getattr(self, c.name) for c in self.__table__.columns }

class Network(db.Model):
    __tablename__ = 'networks'

    id = db.Column(db.Unicode, primary_key=True)

    title = db.Column(db.Unicode, nullable=False)
    description = db.Column(db.UnicodeText)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

class Gateway(db.Model):
    __tablename__ = 'gateways'

    id = db.Column(db.Unicode, primary_key=True)

    network_id = db.Column(db.Unicode, db.ForeignKey('networks.id'), nullable=False)
    network = db.relationship(Network, backref=backref('gateways', lazy='dynamic'))

    title = db.Column(db.Unicode, nullable=False)
    description = db.Column(db.UnicodeText)

    contact_email = db.Column(db.Unicode)
    contact_number = db.Column(db.Unicode)

    url_home = db.Column(db.Unicode)
    url_facebook = db.Column(db.Unicode)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

class Voucher(db.Model):
    __tablename__ = 'vouchers'

    id = db.Column(db.Unicode, primary_key=True, default=generate_id)
    minutes = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    started_at = db.Column(db.DateTime)
    gw_address = db.Column(db.Unicode(15))
    gw_port = db.Column(db.Integer)

    gateway_id = db.Column(db.Unicode, db.ForeignKey('gateways.id'), nullable=False)
    gateway = db.relationship(Gateway, backref=backref('vouchers', lazy='dynamic'))

    mac = db.Column(db.Unicode(20))
    ip = db.Column(db.Unicode(15))
    url = db.Column(db.Unicode(255))
    email = db.Column(db.Unicode(255))
    token = db.Column(db.Unicode(255))
    incoming = db.Column(db.BigInteger, default=0)
    outgoing = db.Column(db.BigInteger, default=0)

    def __repr__(self):
        return '<Voucher %r>' % self.id

    def to_dict(self):
        return { c.name: getattr(self, c.name) for c in self.__table__.columns }

class Auth(db.Model):
    __tablename__ = 'auths'

    id = db.Column(db.Integer, primary_key=True)
    user_agent = db.Column(db.Unicode(255))
    stage = db.Column(db.Unicode)
    ip = db.Column(db.Unicode(20))
    mac = db.Column(db.Unicode(20))
    token = db.Column(db.Unicode)
    incoming = db.Column(db.BigInteger)
    outgoing = db.Column(db.BigInteger)

    gateway_id = db.Column(db.Unicode, db.ForeignKey('gateways.id'), nullable=False)
    gateway = db.relationship(Gateway, backref=backref('auths', lazy='dynamic'))

    status = db.Column(db.Integer)
    messages = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<Auth %r>' % self.id

    def to_dict(self):
        return { c.name: getattr(self, c.name) for c in self.__table__.columns }

    def process_request(self):
        if self.token is None:
            return (constants.AUTH_DENIED, 'No connection token provided')

        voucher = Voucher.query.filter_by(token=self.token).first()

        if voucher is None:
            return (constants.AUTH_DENIED, 'Requested token not found: %s' % self.token)

        if voucher.ip is None:
            voucher.ip = flask.request.args.get('ip')
            db.session.commmit()

        if self.stage == STAGE_LOGIN:
            if voucher.started_at is None:
                if voucher.created_at + datetime.timedelta(minutes=app.config.get('VOUCHER_MAXAGE')) < datetime.datetime.utcnow():
                    db.session.delete(voucher)
                    return (constants.AUTH_DENIED, 'Token is unused but too old: %s' % self.token)

                voucher.started_at = datetime.datetime.utcnow()
                db.session.commit()

                return (constants.AUTH_ALLOWED, None)
            else:
                if voucher.gateway_id == self.gateway_id and voucher.mac == self.mac and voucher.ip == self.ip:
                    if voucher.started_at + datetime.timedelta(minutes=voucher.minutes) < datetime.datetime.utcnow():
                        db.session.delete(voucher)
                        return (constants.AUTH_DENIED, 'Token is in use but has expired: %s' % self.token)
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

                db.session.commit()
            else:
                messages += '| Incoming or outgoing counter is missing; counters not updated'

            if self.stage == constants.STAGE_LOGOUT:
                db.session.delete(voucher)
                messages += '| User is now logged out'
            else:
                if voucher.started_at + datetime.timedelta(minutes=voucher.minutes) < datetime.datetime.utcnow():
                    db.session.delete(voucher)
                    return (constants.AUTH_DENIED, 'Token has expired: %s' % self.token)

            return (constants.AUTH_ALLOWED, messages)
        else:
            return (constants.AUTH_ERROR, 'Unknown stage: %s' % self.stage)

class Ping(db.Model):
    __tablename__ = 'pings'

    id = db.Column(db.Integer, primary_key=True)
    user_agent = db.Column(db.Unicode(255))

    gateway_id = db.Column(db.Unicode, db.ForeignKey('gateways.id'), nullable=False)
    gateway = db.relationship(Gateway, backref=backref('pings', lazy='dynamic'))

    sys_uptime = db.Column(db.BigInteger)
    sys_memfree = db.Column(db.BigInteger)
    sys_load = db.Column(db.Numeric(5, 2))
    wifidog_uptime = db.Column(db.BigInteger)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<Ping %r>' % self.id

    def to_dict(self):
        return { c.name: getattr(self, c.name) for c in self.__table__.columns }

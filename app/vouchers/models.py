import base64
import datetime
import re
import string
import uuid

from app import db, api
from flask.ext.potion import fields
from flask.ext.potion.contrib.principals import PrincipalResource
from random import choice

chars = string.letters + string.digits

def generate_token():
    return uuid.uuid4().hex

def generate_id():
    source = ''.join(choice(chars) for _ in range(4))
    encoded = base64.b32encode(source)
    result = unicode(re.sub(r'=*$', '', encoded))
    return result

class Voucher(db.Model):
    __tablename__ = 'vouchers'

    id = db.Column(db.Unicode, primary_key=True, default=generate_id)
    minutes = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    started_at = db.Column(db.DateTime)
    gw_address = db.Column(db.String(15))
    gw_port = db.Column(db.Integer)
    gateway_id = db.Column(db.Unicode, db.ForeignKey('gateways.id'))
    mac = db.Column(db.String(20))
    ip = db.Column(db.String(15))
    url = db.Column(db.String(255))
    email = db.Column(db.String(255))
    token = db.Column(db.String(255))
    incoming = db.Column(db.BigInteger, default=0)
    outgoing = db.Column(db.BigInteger, default=0)

    def __repr__(self):
        return '<Voucher %r>' % self.id

    def to_dict(self):
        return { c.name: getattr(self, c.name) for c in self.__table__.columns }

admin_roles = [ 'super-admin', 'network-admin', 'gateway-admin' ]

class VoucherResource(PrincipalResource):
    class Meta:
        model = Voucher
        include_id = True
        id_converter = 'string'
        id_field_class = fields.String
        permissions = {
            'read': admin_roles,
            'create': admin_roles,
            'update': admin_roles,
            'delete': admin_roles,
        }
        read_only_fields = [ 'created_at' ]

api.add_resource(VoucherResource)

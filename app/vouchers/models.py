import base64
import datetime
import re
import string
import uuid

from app import db, api_manager
from marshmallow import Schema, fields
from random import choice

chars = string.letters + string.digits

def generate_id():
    source = ''.join(choice(chars) for _ in range(4))
    encoded = base64.b32encode(source)
    result = re.sub(r'=*$', '', encoded)
    return result

class Voucher(db.Model):
    __tablename__ = 'vouchers'

    id = db.Column(db.Integer, primary_key=True)
    voucher = db.Column(db.String(255), default=generate_id)
    minutes = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    started_at = db.Column(db.DateTime)
    gw_address = db.Column(db.String(15))
    gw_port = db.Column(db.Integer)
    gw_id = db.Column(db.String(12))
    mac = db.Column(db.String(20))
    ip = db.Column(db.String(15))
    url = db.Column(db.String(255))
    email = db.Column(db.String(255))
    token = db.Column(db.String(255))
    incoming = db.Column(db.BigInteger, default=0)
    outgoing = db.Column(db.BigInteger, default=0)

    def __init__(self, minutes):
        self.minutes = minutes

    def __repr__(self):
        return '<Voucher %r>' % self.id

    def to_dict(self):
        return { c.name: getattr(self, c.name) for c in self.__table__.columns }

    @staticmethod
    def generate_token():
        return uuid.uuid4().hex

class VoucherSchema(Schema):
    id = fields.Str()
    voucher = fields.Str()
    minutes = fields.Int()
    created_at = fields.DateTime()
    started_at = fields.DateTime()
    gw_address = fields.Str()
    gw_port = fields.Int()
    gw_id = fields.Str()
    mac = fields.Str()
    ip = fields.Str()
    url = fields.Str()
    email = fields.Str()
    token = fields.Str()

    def make_object(self, data):
        return Voucher(**data)

api_manager.create_api(Voucher,
        collection_name='vouchers',
        methods=[ 'GET', 'POST', 'DELETE' ],
        allow_delete_many=True)

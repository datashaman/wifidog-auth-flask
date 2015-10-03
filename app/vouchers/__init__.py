import datetime
import flask
import string
import uuid

from app import app, db, manager
from app.utils import is_logged_in
from flask.ext.login import login_required
from flask.ext.menu import register_menu
from marshmallow import Schema, fields
from random import choice
from sqlalchemy import func, text
from wtforms import Form, HiddenField, PasswordField, TextField, validators

bp = flask.Blueprint('vouchers', __name__, url_prefix='/vouchers', template_folder='templates', static_folder='static')

def args_get(which):
    def func():
        return flask.request.args.get(which)
    return func

class VoucherForm(Form):
    voucher = TextField('Voucher', [ validators.InputRequired() ], default=args_get('voucher'))
    email = TextField('Email Address', [ validators.InputRequired(), validators.Email() ])

    gw_address = HiddenField('Gateway Address', default=args_get('gw_address'))
    gw_port = HiddenField('Gateway Port', default=args_get('gw_port'))
    gw_id = HiddenField('Gateway ID', default=args_get('gw_id'))
    mac = HiddenField('MAC', default=args_get('mac'))
    url = HiddenField('URL', default=args_get('url'))

    def validate_voucher(form, field):
        voucher = Voucher.query.get(field.data)

        if voucher is None:
            raise validators.ValidationError('Voucher does not exist')

        if voucher.started_at is not None:
            raise validators.ValidationError('Voucher is in use')

chars = string.letters + string.digits
length = 8

def generate_id():
    return ''.join(choice(chars) for _ in range(length))

class Voucher(db.Model):
    __tablename__ = 'vouchers'

    id = db.Column(db.String(255), primary_key=True, default=generate_id)
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

@bp.route('/')
@login_required
@register_menu(bp, '.vouchers', 'Vouchers', visible_when=is_logged_in)
def index():
    schema = VoucherSchema(many=True)
    vouchers = schema.dump(Voucher.query.all()).data

    if flask.request.is_xhr:
        return flask.jsonify(vouchers=vouchers)
    else:
        return flask.render_template('vouchers/index.html', vouchers=vouchers)

@bp.route('/', methods=[ 'POST' ])
def create():
    voucher = Voucher(flask.request.form['minutes'])
    db.session.add(voucher)
    db.session.commit()
    return ('', 200)

@bp.route('/', methods=[ 'DELETE' ])
def remove_all():
    Voucher.query.delete()
    db.session.commit()
    return ('', 200)

@bp.route('/<id>', methods=[ 'DELETE' ])
def remove(id):
    Voucher.query.filter_by(id=id).delete()
    db.session.commit()
    return ('', 200)

@manager.command
def expire_vouchers():
    # Vouchers that are in use and have expired
    sql = "delete from vouchers where datetime(started_at, '+' || minutes || ' minutes') < current_timestamp"
    db.engine.execute(text(sql))
    
    # Old vouchers that have not been used yet
    sql = "delete from vouchers where datetime(created_at, '+' || %d || ' minutes') < current_timestamp and started_at is null" % app.config.get('VOUCHER_MAXAGE', 120)
    db.engine.execute(text(sql))

import flask
import uuid

from app import app, db, manager
from app.utils import is_logged_in, args_get
from flask.ext.login import login_required
from flask.ext.menu import register_menu
from wtforms import Form, HiddenField, PasswordField, TextField, validators

from .models import Voucher, VoucherSchema

bp = flask.Blueprint('vouchers', __name__, url_prefix='/vouchers', template_folder='templates', static_folder='static')

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

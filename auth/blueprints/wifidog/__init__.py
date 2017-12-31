import datetime

from auth.models import \
    db, \
    Gateway, \
    Voucher
from auth.services import logos
from auth.utils import args_get, generate_uuid, redirect_url
from auth.vouchers import process_auth
from flask import \
    abort, \
    Blueprint, \
    flash, \
    redirect, \
    render_template, \
    request, \
    session
from flask_wtf import FlaskForm
from sqlalchemy import func
from wtforms import fields as f, validators


wifidog = Blueprint('wifidog', __name__, template_folder='templates')


class WifidogLoginForm(FlaskForm):
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


@wifidog.route('/login/', methods=['GET', 'POST'])
def login():
    form = WifidogLoginForm(request.form)

    if form.validate_on_submit():
        voucher_code = form.voucher_code.data.upper()
        voucher = Voucher.query.filter(func.upper(Voucher.code) == voucher_code, Voucher.status == 'new').first()

        if voucher is None:
            flash(
                'Voucher not found, did you type the code correctly?',
                'error'
            )

            return redirect(redirect_url())

        form.populate_obj(voucher)
        voucher.token = generate_uuid()
        db.session.commit()

        session['next_url'] = form.url.data
        session['voucher_token'] = voucher.token

        url = ('http://%s:%s/wifidog/auth?token=%s' %
               (voucher.gw_address,
                voucher.gw_port,
                voucher.token))

        return redirect(url)

    if request.method == 'GET':
        gw_id = request.args.get('gw_id')
    else:
        gw_id = form.gw_id.data

    if gw_id is None:
        abort(404)

    gateway = Gateway.query.filter_by(id=gw_id).first_or_404()

    return render_template('wifidog/login.html', form=form, gateway=gateway)


@wifidog.route('/ping/')
def ping():
    gateway = Gateway.query.filter_by(id=request.args.get('gw_id')).first_or_404()

    gateway.last_ping_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    gateway.last_ping_at = datetime.datetime.utcnow()
    gateway.last_ping_user_agent = request.user_agent.string
    gateway.last_ping_sys_uptime = request.args.get('sys_uptime')
    gateway.last_ping_wifidog_uptime = request.args.get('wifidog_uptime')
    gateway.last_ping_sys_memfree = request.args.get('sys_memfree')
    gateway.last_ping_sys_load = request.args.get('sys_load')

    db.session.commit()

    return ('Pong', 200)


@wifidog.route('/auth/')
def auth():
    args = dict(
        user_agent=request.user_agent.string,
        stage=request.args.get('stage'),
        ip=request.args.get('ip'),
        mac=request.args.get('mac'),
        token=request.args.get('token'),
        incoming=int(request.args.get('incoming')),
        outgoing=int(request.args.get('outgoing')),
        gateway_id=request.args.get('gw_id'),
    )
    (status, messages) = process_auth(args)
    return "Auth: %s\nMessages: %s\n" % (status, messages), 200


@wifidog.route('/portal/')
def portal():
    voucher_token = session.get('voucher_token')
    if voucher_token:
        voucher = Voucher.query.filter_by(token=voucher_token).first()
    else:
        voucher = None
    gw_id = request.args.get('gw_id')
    if gw_id is None:
        abort(404)
    gateway = Gateway.query.filter_by(id=gw_id).first_or_404()
    logo_url = None
    if gateway.logo:
        logo_url = logos.url(gateway.logo)
    next_url = session.pop('next_url', None)
    return render_template('wifidog/portal.html',
                           gateway=gateway,
                           logo_url=logo_url,
                           next_url=next_url,
                           voucher=voucher)

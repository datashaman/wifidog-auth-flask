import flask

from app import db
from app.vouchers.forms import VoucherForm
from app.wifidog.models import Auth, Ping

bp = flask.Blueprint('wifidog', __name__, url_prefix='/wifidog', template_folder='templates', static_folder='static')

@bp.route('/login/', methods=[ 'GET', 'POST' ])
def login():
    form = VoucherForm(flask.request.form)

    if flask.request.method == 'POST' and form.validate():
        voucher = Voucher.query.filter_by(voucher=form.voucher.data).first_or_404()

        if voucher.started_at is None:
            voucher.gw_address = form.gw_address.data
            voucher.gw_port = form.gw_port.data
            voucher.gw_id = form.gw_id.data
            voucher.ip = form.ip.data
            voucher.mac = form.mac.data
            voucher.url = form.url.data
            voucher.email = form.email.data
            voucher.token = Voucher.generate_token()
            db.session.commit()

            url = 'http://%s:%s/wifidog/auth?token=%s' % (voucher.gw_address, voucher.gw_port, voucher.token)
            return flask.redirect(url)

    return flask.render_template('wifidog/login.html', form=form)

@bp.route('/ping/')
def ping():
    ping = Ping(
        user_agent=flask.request.user_agent.string,
        gw_id=flask.request.args.get('gw_id'),
        sys_uptime=flask.request.args.get('sys_uptime'),
        sys_memfree=flask.request.args.get('sys_memfree'),
        sys_load=flask.request.args.get('sys_load'),
        wifidog_uptime=flask.request.args.get('wifidog_uptime')
    )
    db.session.add(ping)
    db.session.commit()
    return ('Pong', 200)

@bp.route('/auth/')
def auth():
    auth = Auth(
        user_agent=flask.request.user_agent.string,
        stage=flask.request.args.get('stage'),
        ip=flask.request.args.get('ip'),
        mac=flask.request.args.get('mac'),
        token=flask.request.args.get('token'),
        incoming=flask.request.args.get('incoming'),
        outgoing=flask.request.args.get('outgoing')
    )

    (auth.status, auth.messages) = auth.process_request()

    db.session.add(auth)
    db.session.commit()

    return ("Auth: %s\nMessages: %s\n" % (auth.status, auth.messages), 200)

@bp.route('/portal/')
def portal():
    gw_id = flask.request.args.get('gw_id')
    return flask.render_template('wifidog/portal.html', gw_id=gw_id)

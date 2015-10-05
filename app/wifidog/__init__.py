import datetime
import flask

from app import app, db, manager
from app.vouchers import Voucher, VoucherForm
from flask.ext.menu import register_menu

bp = flask.Blueprint('wifidog', __name__, url_prefix='/wifidog', template_folder='templates', static_folder='static')

class Ping(db.Model):
    __tablename__ = 'pings'

    id = db.Column(db.Integer, primary_key=True)
    user_agent = db.Column(db.String(255))
    gw_id = db.Column(db.String(12))
    sys_uptime = db.Column(db.BigInteger)
    sys_memfree = db.Column(db.BigInteger)
    sys_load = db.Column(db.Numeric(5, 2))
    wifidog_uptime = db.Column(db.BigInteger)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __init__(self, user_agent, gw_id, sys_uptime, sys_memfree, sys_load, wifidog_uptime):
        self.user_agent = user_agent
        self.gw_id = gw_id
        self.sys_uptime = sys_uptime
        self.sys_memfree = sys_memfree
        self.sys_load = sys_load
        self.wifidog_uptime = wifidog_uptime

    def __repr__(self):
        return '<Ping %r>' % self.id

    def to_dict(self):
        return { c.name: getattr(self, c.name) for c in self.__table__.columns }

STAGE_LOGIN = 'login'
STAGE_LOGOUT = 'logout'
STAGE_COUNTERS = 'counters'

AUTH_DENIED = 0
AUTH_VALIDATION_FAILED = 6
AUTH_ALLOWED = 1
AUTH_VALIDATION = 5
AUTH_ERROR = -1

class Auth(db.Model):
    __tablename__ = 'auths'

    id = db.Column(db.Integer, primary_key=True)
    user_agent = db.Column(db.String(255))
    stage = db.Column(db.String)
    ip = db.Column(db.String(20))
    mac = db.Column(db.String(20))
    token = db.Column(db.String)
    incoming = db.Column(db.BigInteger)
    outgoing = db.Column(db.BigInteger)
    gw_id = db.Column(db.String(20))
    status = db.Column(db.Integer)
    messages = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __init__(self, user_agent, stage, ip, mac, token, incoming, outgoing):
        self.user_agent = user_agent
        self.stage = stage
        self.ip = ip
        self.mac = mac
        self.token = token
        self.incoming = incoming
        self.outgoing = outgoing

    def __repr__(self):
        return '<Auth %r>' % self.id

    def to_dict(self):
        return { c.name: getattr(self, c.name) for c in self.__table__.columns }

    def process_request(self):
        if self.token is None:
            return (AUTH_DENIED, 'No connection token provided')

        voucher = Voucher.query.filter_by(token=self.token).first()

        if voucher is None:
            return (AUTH_DENIED, 'Requested token not found: %s' % self.token)

        if voucher.ip is None:
            voucher.ip = flask.request.args.get('ip')
            db.session.commmit()

        if self.stage == STAGE_LOGIN:
            if voucher.started_at is None:
                if voucher.created_at + datetime.timedelta(minutes=app.config.get('VOUCHER_MAXAGE')) < datetime.datetime.utcnow():
                    db.session.delete(voucher)
                    return (AUTH_DENIED, 'Token is unused but too old: %s' % self.token)

                voucher.started_at = datetime.datetime.utcnow()
                db.session.commit()

                return (AUTH_ALLOWED, None)
            else:
                if voucher.gw_id == self.gw_id and voucher.mac == self.mac and voucher.ip == self.ip:
                    if voucher.started_at + datetime.timedelta(minutes=voucher.minutes) < datetime.datetime.utcnow():
                        db.session.delete(voucher)
                        return (AUTH_DENIED, 'Token is in use but has expired: %s' % self.token)
                    else:
                        return (AUTH_ALLOWED, 'Token is already in use but details match: %s' % self.token)
                else:
                    return (AUTH_DENIED, 'Token is already in use: %s' % self.token)
        elif self.stage in [ STAGE_LOGOUT, STAGE_COUNTERS ]:
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

            if self.stage == STAGE_LOGOUT:
                db.session.delete(voucher)
                messages += '| User is now logged out'
            else:
                if voucher.started_at + datetime.timedelta(minutes=voucher.minutes) < datetime.datetime.utcnow():
                    db.session.delete(voucher)
                    return (AUTH_DENIED, 'Token has expired: %s' % self.token)

            return (AUTH_ALLOWED, messages)
        else:
            return (AUTH_ERROR, 'Unknown stage: %s' % self.stage)

@bp.route('/login/', methods=[ 'GET', 'POST' ])
@register_menu(bp, '.login', 'Use Voucher')
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
        flask.request.user_agent.string,
        flask.request.args.get('gw_id'),
        flask.request.args.get('sys_uptime'),
        flask.request.args.get('sys_memfree'),
        flask.request.args.get('sys_load'),
        flask.request.args.get('wifidog_uptime')
    )
    db.session.add(ping)
    db.session.commit()
    return ('Pong', 200)

@bp.route('/auth/')
def auth():
    auth = Auth(
        flask.request.user_agent.string,
        flask.request.args.get('stage'),
        flask.request.args.get('ip'),
        flask.request.args.get('mac'),
        flask.request.args.get('token'),
        flask.request.args.get('incoming'),
        flask.request.args.get('outgoing')
    )

    (auth.status, auth.messages) = auth.process_request()

    db.session.add(auth)
    db.session.commit()

    return ("Auth: %s\nMessages: %s\n" % (auth.status, auth.messages), 200)

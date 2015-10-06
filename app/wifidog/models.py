import datetime
import flask

from app import app, db
from app.wifidog import constants

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
    gateway_id = db.Column(db.Unicode)
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
    user_agent = db.Column(db.String(255))
    gateway_id = db.Column(db.Unicode)
    sys_uptime = db.Column(db.BigInteger)
    sys_memfree = db.Column(db.BigInteger)
    sys_load = db.Column(db.Numeric(5, 2))
    wifidog_uptime = db.Column(db.BigInteger)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<Ping %r>' % self.id

    def to_dict(self):
        return { c.name: getattr(self, c.name) for c in self.__table__.columns }

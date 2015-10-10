import flask
import json

from app import app
from app.forms import NetworkForm
from app.models import Network
from app.services import db
from app.utils import is_logged_in, has_role, has_a_role
from flask.ext.menu import register_menu
from flask.ext.security import login_required, roles_required, roles_accepted, current_user

@app.route('/networks')
@login_required
@roles_required('super-admin')
@register_menu(app, '.networks', 'Networks', visible_when=has_role('super-admin'), order=10)
def networks_index():
    return flask.render_template('networks/index.html')

@app.route('/networks/new', methods=[ 'GET', 'POST' ])
@login_required
@roles_required('super-admin')
def networks_new():
    network = Network()
    form = NetworkForm(flask.request.form, network)

    if form.validate_on_submit():
        form.populate_obj(network)
        db.session.add(network)
        db.session.commit()

        flask.flash('Network created')

        return flask.redirect(flask.url_for('.index'))

    return flask.render_template('networks/edit.html', form=form, network=network)

@app.route('/networks/<network_id>', methods=[ 'GET', 'POST' ])
@login_required
@roles_required('super-admin')
def networks_edit(network_id):
    network = Network.query.filter_by(id=network_id).first_or_404()
    form = NetworkForm(flask.request.form, network)

    if form.validate_on_submit():
        form.populate_obj(network)
        db.session.add(network)
        db.session.commit()

        flask.flash('Network updated')

        return flask.redirect(flask.url_for('.index'))

    return flask.render_template('networks/edit.html', form=form, network=network)

@app.route('/gateways')
@login_required
@roles_accepted('super-admin', 'network-admin')
@register_menu(app, '.gateways', 'Gateways', visible_when=has_a_role('super-admin', 'network-admin'), order=20)
def gateways_index():
    return flask.render_template('gateways/index.html')

@app.route('/users')
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
@register_menu(app, '.users', 'Users', visible_when=has_a_role('super-admin', 'network-admin', 'gateway-admin'), order=40)
def users_index():
    return flask.render_template('users/index.html')

@app.route('/vouchers')
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
@register_menu(app, '.vouchers', 'Vouchers', visible_when=has_a_role('super-admin', 'network-admin', 'gateway-admin'), order=30)
def vouchers_index():
    return flask.render_template('vouchers/index.html')

@app.route('/wifidog/login/', methods=[ 'GET', 'POST' ])
def wifidog_login():
    form = VoucherForm(flask.request.form)

    if flask.request.method == 'POST' and form.validate():
        voucher = Voucher.query.filter_by(id=form.voucher.data).first_or_404()

        if voucher.started_at is None:
            voucher.gw_address = form.gw_address.data
            voucher.gw_port = form.gw_port.data
            voucher.gateway_id = form.gateway_id.data
            voucher.mac = form.mac.data
            voucher.url = form.url.data
            voucher.email = form.email.data
            voucher.token = generate_token()
            db.session.commit()

            url = 'http://%s:%s/wifidog/auth?token=%s' % (voucher.gw_address, voucher.gw_port, voucher.token)
            return flask.redirect(url)

    if flask.request.method == 'GET':
        gateway_id = flask.request.args.get('gw_id')
    else:
        gateway_id = form.gateway_id.data

    if gateway_id is None:
        flask.abort(404)

    gateway = Gateway.query.filter_by(id=gateway_id).first_or_404()
    return flask.render_template('wifidog/login.html', form=form, gateway=gateway)

@app.route('/wifidog/ping/')
def wifidog_ping():
    ping = Ping(
        user_agent=flask.request.user_agent.string,
        gateway_id=flask.request.args.get('gw_id'),
        sys_uptime=flask.request.args.get('sys_uptime'),
        sys_memfree=flask.request.args.get('sys_memfree'),
        sys_load=flask.request.args.get('sys_load'),
        wifidog_uptime=flask.request.args.get('wifidog_uptime')
    )
    db.session.add(ping)
    db.session.commit()
    return ('Pong', 200)

@app.route('/wifidog/auth/')
def wifidog_auth():
    voucher = Voucher.query.filter_by(token=flask.request.args.get('token')).first_or_404()

    auth = Auth(
        user_agent=flask.request.user_agent.string,
        stage=flask.request.args.get('stage'),
        ip=flask.request.args.get('ip'),
        mac=flask.request.args.get('mac'),
        token=flask.request.args.get('token'),
        incoming=flask.request.args.get('incoming'),
        outgoing=flask.request.args.get('outgoing'),
        voucher_id=voucher.id
    )

    (auth.status, auth.messages) = auth.process_request()

    db.session.add(auth)
    db.session.commit()

    return ("Auth: %s\nMessages: %s\n" % (auth.status, auth.messages), 200)

@app.route('/wifidog/portal/')
def wifidog_portal():
    gateway = Gateway.query.filter_by(id=flask.request.args.get('gw_id')).first_or_404()
    return flask.render_template('wifidog/portal.html', gateway=gateway)

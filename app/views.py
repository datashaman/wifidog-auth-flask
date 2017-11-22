"""
Views for the app
"""

from __future__ import absolute_import
from __future__ import division

import uuid

from app import constants

from app.forms import \
    CategoryForm, \
    CurrencyForm, \
    GatewayForm, \
    LoginVoucherForm, \
    MyUserForm, \
    NetworkForm, \
    NewVoucherForm, \
    ProductForm, \
    UserForm

from app.models import Auth, Ping, db
from app.payu import get_transaction, set_transaction, capture
from app.resources import api
from app.signals import voucher_logged_in
from app.utils import is_logged_in, has_a_role

from flask import \
    Blueprint, \
    abort, \
    current_app, \
    flash, \
    jsonify, \
    redirect, \
    request, \
    render_template, \
    session, \
    url_for
from flask_menu import register_menu
from flask_potion.exceptions import ItemNotFound
from flask_potion.instances import COMPARATORS, Condition
from flask_security import \
    current_user, \
    login_required, \
    roles_accepted, \
    roles_required


bp = Blueprint('app', __name__)


def generate_token():
    """Generate token for the voucher session"""
    return uuid.uuid4().hex


def read_or_404(resource, id):
    """
    Return instance found via resource manager,
    abort with 404 if not found
    """
    try:
        return api.resources[resource].manager.read(id)
    except ItemNotFound:
        abort(404)


def resource_instances(resource):
    """Return instances found via resource manager"""
    return api.resources[resource].manager.instances()


def resource_index(resource, form=None):
    """Handle a resource index request"""
    instances = resource_instances(resource)
    return render_template('%s/index.html' % resource,
                           form=form,
                           instances=instances)


def resource_new(resource, form_class):
    """Handle a new resource request"""
    form = form_class()
    if form.validate_on_submit():
        instance = api.resources[resource].manager.create(form.data)
        flash('Create %s successful' % instance)
        return redirect(url_for('.%s_index' % resource))
    return render_template('%s/new.html' % resource, form=form)


def resource_edit(resource, id, form_class):
    instance = read_or_404(resource, id)
    form = form_class(obj=instance)
    if form.validate_on_submit():
        instance = api.resources[resource].manager.update(instance, form.data)
        flash('Update %s successful' % instance)
        return redirect(url_for('.%s_index' % resource))
    return render_template('%s/edit.html' % resource,
                           form=form,
                           instance=instance)


def resource_show(resource, id):
    instance = read_or_404(resource, id)
    return render_template('%s/show.html' % resource, instance=instance)


def resource_delete(resource, id):
    instance = read_or_404(resource, id)
    if request.method == 'POST':
        api.resources[resource].manager.delete(instance)
        flash('Delete %s successful' % instance)
        return redirect(url_for('.%s_index' % resource))
    return render_template('shared/delete.html',
                           instance=instance,
                           resource=resource)


def resource_action(resource, id, action):
    instance = read_or_404(resource, id)
    if request.method == 'POST':
        if action in constants.ACTIONS[resource]:
            getattr(api.resources[resource].manager, action)(instance)
            flash('%s %s successful' % (instance, action))
            return redirect(url_for('.%s_index' % resource))
        else:
            abort(404)
    return render_template('shared/action.html',
                           instance=instance,
                           action=action,
                           resource=resource)


@bp.route('/network', methods=['GET', 'POST'])
@login_required
@roles_accepted('network-admin')
@register_menu(
    bp,
    '.network',
    'My Network',
    visible_when=has_a_role('network-admin'),
    order=10
)
def my_network():
    form = NetworkForm(obj=current_user.network)
    if form.validate_on_submit():
        api.resources['networks'].update(current_user.network, form.data)
        flash('Update successful')
        return redirect('/')
    return render_template('networks/current.html',
                           form=form,
                           instance=current_user.network)


@bp.route('/gateway', methods=['GET', 'POST'])
@login_required
@roles_accepted('gateway-admin')
@register_menu(
    bp,
    '.gateway',
    'My Gateway',
    visible_when=has_a_role('gateway-admin'),
    order=10
)
def my_gateway():
    form = GatewayForm(obj=current_user.gateway)
    if form.validate_on_submit():
        api.resources['gateways'].manager.update(current_user.gateway,
                                                 form.data)
        flash('Update successful')
        return redirect('/')
    return render_template('gateways/current.html',
                           form=form,
                           instance=current_user.gateway)


@bp.route('/user', methods=['GET', 'POST'])
@login_required
@register_menu(
    bp,
    '.account',
    'My Account',
    visible_when=is_logged_in,
    order=10
)
def my_account():
    form = MyUserForm(obj=current_user)
    if form.validate_on_submit():
        if form.password.data == '':
            del form.password
        api.resources['users'].manager.update(current_user, form.data)
        flash('Update successful')
        return redirect('/')
    return render_template('users/current.html',
                           form=form,
                           instance=current_user)


@bp.route('/networks')
@login_required
@roles_accepted('super-admin')
@register_menu(
    bp,
    '.networks',
    'Networks',
    visible_when=has_a_role('super-admin'),
    order=10
)
def networks_index():
    return resource_index('networks')


@bp.route('/networks/new', methods=['GET', 'POST'])
@login_required
@roles_required('super-admin')
def networks_new():
    return resource_new('networks', NetworkForm)


@bp.route('/networks/<id>', methods=['GET', 'POST'])
@login_required
@roles_required('super-admin')
def networks_edit(id):
    return resource_edit('networks', id, NetworkForm)


@bp.route('/networks/<id>/delete', methods=['GET', 'POST'])
@login_required
@roles_required('super-admin')
def networks_delete(id):
    return resource_delete('networks', id)


@bp.route('/gateways')
@login_required
@roles_accepted('super-admin', 'network-admin')
@register_menu(
    bp,
    '.gateways',
    'Gateways',
    visible_when=has_a_role('super-admin', 'network-admin'),
    order=20)
def gateways_index():
    return resource_index('gateways')


@bp.route('/gateways/new', methods=['GET', 'POST'])
@login_required
@roles_required('super-admin')
def gateways_new():
    return resource_new('gateways', GatewayForm)


@bp.route('/gateways/<id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin')
def gateways_edit(id):
    return resource_edit('gateways', id, GatewayForm)


@bp.route('/gateways/<id>/delete', methods=['GET', 'POST'])
@login_required
@roles_required('super-admin')
def gateways_delete(id):
    return resource_delete('gateways', id)


@bp.route('/users')
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
@register_menu(
    bp,
    '.users',
    'Users',
    visible_when=has_a_role('super-admin', 'network-admin', 'gateway-admin'),
    order=40
)
def users_index():
    form = UserForm()
    return resource_index('users', form=form)


@bp.route('/users/new', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin')
def users_new():
    return resource_new('users', UserForm)


@bp.route('/users/<id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def users_edit(id):
    instance = read_or_404('users', id)

    if (current_user.has_role('network-admin')
            and instance.network != current_user.network):
        abort(403)

    if (current_user.has_role('gateway-admin')
            and (instance.network != current_user.network
                 or instance.gateway != current_user.gateway)):
        abort(403)

    form = UserForm(obj=instance)

    if current_user.has_role('network-admin'):
        del form.gateway

    if current_user == instance:
        del form.active
        del form.roles

    if form.validate_on_submit():
        if form.password.data == '':
            del form.password

        instance = api.resources['users'].manager.update(instance, form.data)
        flash('Update %s successful' % instance)
        return redirect(url_for('.users_index'))
    return render_template('users/edit.html', form=form, instance=instance)


@bp.route('/users/<id>/delete', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin')
def users_delete(id):
    return resource_delete('users', id)


@bp.route('/vouchers')
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
@register_menu(
    bp,
    '.vouchers',
    'Vouchers',
    visible_when=has_a_role('super-admin', 'network-admin', 'gateway-admin'),
    order=5
)
def vouchers_index():
    return resource_index('vouchers')


@bp.route('/vouchers/<id>/<action>', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def vouchers_action(id, action):
    return resource_action('vouchers', id, action)


@bp.route('/categories')
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
@register_menu(
    bp,
    '.categories',
    'Categories',
    visible_when=has_a_role('super-admin', 'network-admin', 'gateway-admin'),
    order=99
)
def categories_index():
    return resource_index('categories')


@bp.route('/categories/new', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def categories_new():
    return resource_new('categories', CategoryForm)


@bp.route('/categories/<id>/delete', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def categories_delete(id):
    return resource_delete('categories', id)


@bp.route('/categories/<id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def categories_edit(id):
    return resource_edit('categories', id, CategoryForm)


@bp.route('/products')
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
@register_menu(
    bp,
    '.products',
    'Products',
    visible_when=has_a_role('super-admin', 'network-admin', 'gateway-admin'),
    order=99
)
def products_index():
    return resource_index('products')


@bp.route('/products/new', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def products_new():
    return resource_new('products', ProductForm)


@bp.route('/products/<id>/delete', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def products_delete(id):
    return resource_delete('products', id)


@bp.route('/products/<id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def products_edit(id):
    return resource_edit('products', id, ProductForm)


@bp.route('/currencies')
@login_required
@roles_accepted('super-admin')
@register_menu(
    bp,
    '.currencies',
    'Currencies',
    visible_when=has_a_role('super-admin'),
    order=99
)
def currencies_index():
    return resource_index('currencies')


@bp.route('/currencies/new', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def currencies_new():
    return resource_new('currencies', CurrencyForm)


@bp.route('/currencies/<id>/delete', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def currencies_delete(id):
    return resource_delete('currencies', id)


@bp.route('/currencies/<id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def currencies_edit(id):
    return resource_edit('currencies', id, CurrencyForm)


@bp.route('/new-voucher', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
@register_menu(
    bp,
    '.new-voucher',
    'New Voucher',
    visible_when=has_a_role('super-admin', 'network-admin', 'gateway-admin'),
    order=0
)
def vouchers_new():
    form = NewVoucherForm()
    choices = []

    if current_user.has_role('gateway-admin'):
        choices = [
            [
                current_user.gateway_id,
                '%s - %s' % (current_user.gateway.network.title,
                             current_user.gateway.title)
            ]
        ]
    else:
        if current_user.has_role('network-admin'):
            networks = api.resources['networks'].manager.instances([
                Condition('id', COMPARATORS['$eq'], current_user.network_id),
            ])
        else:
            networks = resource_instances('networks')

        for network in networks:
            for gateway in network.gateways:
                choices.append([
                    gateway.id,
                    '%s - %s' % (network.title,
                                 gateway.title)
                ])

    form.gateway_id.choices = choices

    if form.validate_on_submit():
        voucher = api.resources['vouchers'].manager.create(form.data)
        return redirect(url_for('.vouchers_new', code=voucher.code))

    return render_template('vouchers/new.html', form=form)


@bp.route('/wifidog/login/', methods=['GET', 'POST'])
def wifidog_login():
    form = LoginVoucherForm(request.form)

    if form.validate_on_submit():
        voucher_code = form.voucher_code.data.upper()
        voucher = api.resources['vouchers'].manager.first([
            Condition('code', COMPARATORS['$eq'], voucher_code),
        ])
        data = form.data
        data['token'] = generate_token()
        api.resources['vouchers'].manager.update(voucher, data)

        voucher_logged_in.send(current_app._get_current_object(),
                               voucher=voucher)

        # flash(
        #     'Logged in, continue to <a href="%s">%s</a>'
        #         % (form.url.data, form.url.data),
        #     'success'
        # )

        url = ('http://%s:%s/wifidog/auth?token=%s' %
               (voucher.gw_address,
                voucher.gw_port,
                voucher.token))

        return redirect(url)

    if request.method == 'GET':
        gateway_id = request.args.get('gw_id')
    else:
        gateway_id = form.gateway_id.data

    if gateway_id is None:
        abort(404)

    gateway = read_or_404('gateways', gateway_id)
    return render_template('wifidog/login.html', form=form, gateway=gateway)


@bp.route('/wifidog/ping/')
def wifidog_ping():
    ping = Ping(
        user_agent=request.user_agent.string,
        gateway_id=request.args.get('gw_id'),
        sys_uptime=request.args.get('sys_uptime'),
        sys_memfree=request.args.get('sys_memfree'),
        sys_load=request.args.get('sys_load'),
        wifidog_uptime=request.args.get('wifidog_uptime')
    )

    db.session.add(ping)
    db.session.commit()

    def generate_point(measurement):
        return {
            "measurement": measurement,
            "tags": {
                "source": "ping",
                "network_id": ping.gateway.network_id,
                "gateway_id": ping.gateway_id,
                "user_agent": ping.user_agent,
            },
            "time": ping.created_at,
            "fields": {
                "value": getattr(ping, measurement),
            }
        }

    # points = [
    #     generate_point(m) for m in [
    #         'sys_uptime',
    #         'sys_memfree',
    #         'sys_load',
    #         'wifidog_uptime'
    #     ]
    # ]
    # influx_db.connection.write_points(points)

    return ('Pong', 200)


@bp.route('/wifidog/auth/')
def wifidog_auth():
    auth = Auth(
        user_agent=request.user_agent.string,
        stage=request.args.get('stage'),
        ip=request.args.get('ip'),
        mac=request.args.get('mac'),
        token=request.args.get('token'),
        incoming=request.args.get('incoming'),
        outgoing=request.args.get('outgoing'),
        gateway_id=request.args.get('gw_id')
    )

    (auth.status, auth.messages) = auth.process_request()

    db.session.add(auth)
    db.session.commit()

    def generate_point(measurement):
        return {
            "measurement": 'auth_%s' % measurement,
            "tags": {
                "source": "auth",
                "network_id": auth.gateway.network_id,
                "gateway_id": auth.gateway_id,
                "user_agent": auth.user_agent,
                "stage": auth.stage,
                "ip": auth.ip,
                "mac": auth.mac,
                "token": auth.token,
            },
            "time": auth.created_at,
            "fields": {
                "value": getattr(auth, measurement),
            }
        }

    # points = [generate_point(m) for m in [ 'incoming', 'outgoing' ]]
    # influx_db.connection.write_points(points)

    return ("Auth: %s\nMessages: %s\n" % (auth.status, auth.messages), 200)


@bp.route('/wifidog/portal/')
def wifidog_portal():
    voucher_token = session.get('voucher_token')
    if voucher_token:
        voucher = api.resources['vouchers'].manager.first([
            Condition('token', COMPARATORS['$eq'], voucher_token),
        ])
    else:
        voucher = None
    gateway = read_or_404('gateways', request.args.get('gw_id'))
    return render_template('wifidog/portal.html',
                           gateway=gateway,
                           voucher=voucher)


@bp.route('/pay')
def pay():
    return_url = url_for('.pay_return', _external=True)
    cancel_url = url_for('.pay_cancel', _external=True)
    response = set_transaction('ZAR',
                               1000,
                               'Something',
                               return_url,
                               cancel_url)
    return redirect('%s?PayUReference=%s' % (capture, response.payUReference))


@bp.route('/pay/return')
def pay_return():
    response = get_transaction(request.args.get('PayUReference'))
    basketAmount = '{:.2f}'.format(int(response.basket.amountInCents) / 100)
    category = 'success' if response.successful else 'error'
    flash(response.displayMessage, category)
    return render_template('payu/transaction.html',
                           response=response,
                           basketAmount=basketAmount)


@bp.route('/pay/cancel')
def pay_cancel():
    response = get_transaction(request.args.get('payUReference'))
    basketAmount = '{:.2f}'.format(int(response.basket.amountInCents) / 100)
    flash(response.displayMessage, 'warning')
    return render_template('payu/transaction.html',
                           response=response,
                           basketAmount=basketAmount)


@bp.route('/')
def home():
    return redirect(url_for('security.login'))


@bp.route('/config')
def config():
    return current_app.config['SQLALCHEMY_DATABASE_URI']


@bp.route('/debug')
def debug():
    return jsonify(dict(session))

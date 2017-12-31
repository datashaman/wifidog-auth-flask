"""
Views for the app
"""

from __future__ import absolute_import
from __future__ import division

import os

from auth import constants

from auth.forms import \
    AdjustmentForm, \
    CashupForm, \
    CountryForm, \
    CurrencyForm, \
    ProductForm, \
    SelectCategoryForm, \
    SelectNetworkGatewayForm, \
    TransactionFilterForm

from auth.models import \
    Adjustment, \
    Cashup, \
    Category, \
    Gateway, \
    Network, \
    Product, \
    Transaction, \
    db

from auth.resources import \
        resource_instance, \
        resource_instances, \
        RESOURCE_MODELS
from auth.services import \
        environment_dump, \
        healthcheck as healthcheck_service
from auth.utils import has_role, redirect_url

from flask import \
    Blueprint, \
    abort, \
    current_app, \
    flash, \
    redirect, \
    request, \
    render_template, \
    send_from_directory, \
    url_for
from flask_menu import register_menu
from flask_security import \
    auth_token_required, \
    current_user, \
    login_required, \
    roles_accepted
from wtforms import fields as f, validators


bp = Blueprint('auth', __name__)


def has_admin_role():
    return has_role('super-admin', 'network-admin', 'gateway-admin')


def resource_url_for(resource, verb, **kwargs):
    if resource in [
        'category',
        'gateway',
        'network',
        'order',
        'user',
        'voucher',
    ]:
        return url_for('%s.%s' % (resource, verb), **kwargs)
    else:
        return url_for('.%s_%s' % (resource, verb), **kwargs)


def resource_index(resource, form=None):
    """Handle a resource index request"""
    pagination = resource_instances(resource, form).paginate()
    return render_template('%s/index.html' % resource,
                           form=form,
                           pagination=pagination,
                           resource=resource)


def resource_new(resource, form):
    """Handle a new resource request"""
    if form.validate_on_submit():
        instance = RESOURCE_MODELS[resource]()
        form.populate_obj(instance)
        db.session.add(instance)
        db.session.commit()
        flash('Create %s successful' % instance)
        return redirect(resource_url_for(resource, 'index'))
    return render_template('%s/new.html' % resource,
                           form=form,
                           resource=resource)


def resource_edit(resource, form_class, **kwargs):
    """Handle a resource edit request"""
    instance = resource_instance(resource, **kwargs)
    form = form_class(obj=instance)
    if form.validate_on_submit():
        form.populate_obj(instance)
        db.session.commit()
        flash('Update %s successful' % instance)
        return redirect(resource_url_for(resource, 'index'))
    return render_template('%s/edit.html' % resource,
                           form=form,
                           instance=instance,
                           resource=resource)


def resource_show(resource, **kwargs):
    """Handle a resource show request"""
    instance = resource_instance(resource, **kwargs)
    return render_template('%s/show.html' % resource,
                           instance=instance,
                           resource=resource)


def resource_delete(resource, **kwargs):
    """Handle a resource delete request"""
    instance = resource_instance(resource, **kwargs)
    if request.method == 'POST':
        instance_label = str(instance)
        db.session.delete(instance)
        db.session.commit()
        flash('Delete %s successful' % instance_label)
        return redirect(resource_url_for(resource, 'index'))
    action_url = resource_url_for(resource, 'delete', **kwargs)
    return render_template('shared/delete.html',
                           action_url=action_url,
                           instance=instance,
                           resource=resource)


def resource_action(resource, action, **kwargs):
    """Handle a resource action request"""
    instance = resource_instance(resource, **kwargs)
    if request.method == 'POST':
        if action in constants.ACTIONS[resource]:
            getattr(instance, action)()
            db.session.commit()
            flash('%s %s successful' % (instance, action))
            return redirect(resource_url_for(resource, 'index'))
        else:
            abort(404)
    kwargs['action'] = action
    return render_template('shared/action.html',
                           action=action,
                           action_url=resource_url_for(resource,
                                                       'action',
                                                       **kwargs),
                           instance=instance,
                           resource=resource)


@bp.route('/products')
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
@register_menu(
    bp,
    'products',
    'Products',
    visible_when=has_admin_role(),
    order=80
)
def product_index():
    return resource_index('product')


@bp.route('/products/sort', methods=['POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def product_sort():
    content = request.get_json()
    for product_id, sequence in content['sequences'].items():
        product = Product.query.get_or_404(product_id)
        product.sequence = sequence
        db.session.commit()
    return 'OK'


def get_category_properties(category):
    names = category.properties
    return names.split('\n') if names else []


def set_product_properties(product, names):
    if product.properties:
        lines = product.properties.split('\n')
        for line in lines:
            (k, v) = line.split('=')
            if k in names:
                setattr(product, k, v)


def add_form_fields(form, names):
    for name in names:
        setattr(form,
                name,
                f.StringField(name[0].upper() + name[1:],
                              validators=[
                                  validators.InputRequired(),
                              ],
                              _name=name))


def update_product_properties(product, form, names):
    form.populate_obj(product)
    if names:
        values = {}
        for name in names:
            values[name] = getattr(form, name).data
        product.properties = '\n'.join('%s=%s' % (k, v) for k, v in values.items())


@bp.route('/products/new/<network_id>/<gateway_id>/<category_id>', methods=['GET', 'POST'])
@bp.route('/products/new/<network_id>/<gateway_id>', methods=['GET', 'POST'])
@bp.route('/products/new/<network_id>', methods=['GET', 'POST'])
@bp.route('/products/new', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def product_new(network_id=None, gateway_id=None, category_id=None):
    if network_id is None and gateway_id is None:
        if current_user.has_role('gateway-admin'):
            url = url_for('.product_new',
                          network_id=current_user.network.id,
                          gateway_id=current_user.gateway.id)
            return redirect(url)

        form = SelectNetworkGatewayForm()

        if form.validate_on_submit():
            gateway_id = form.gateway.data.id if form.gateway.data else '__none'
            url = url_for('.product_new',
                          network_id=form.network.data.id,
                          gateway_id=gateway_id)
            return redirect(url)
        return render_template('shared/select-network-gateway.html',
                               action_url=url_for('.product_new'),
                               form=form)

    if current_user.has_role('gateway-admin'):
        if network_id != current_user.network.id or gateway_id != current_user.gateway.id:
            abort(403)

    if current_user.has_role('network-admin'):
        if network_id != current_user.network.id:
            abort(403)

        if gateway_id != '__none' and current_user.network.gateways.filter_by(id=gateway_id).count() == 0:
            abort(403)

    if category_id is None:
        choices = Category.query.filter(Category.network == None, Category.gateway == None).all()

        if network_id:
            choices += Category.query.filter(Category.network_id == network_id,
                                             Category.gateway_id == None).all()

        if network_id and gateway_id:
            choices += Category.query.filter(Category.network_id == network_id,
                                             Category.gateway_id == gateway_id).all()

        form = SelectCategoryForm()

        if form.validate_on_submit():
            gateway_id = '__none' if gateway_id is None else gateway_id
            url = url_for('.product_new', network_id=network_id, gateway_id=gateway_id, category_id=form.category.data.id)
            return redirect(url)

        return render_template('shared/select-category.html',
                               action_url=url_for('.product_new', network_id=network_id, gateway_id=gateway_id),
                               form=form)

    data = {
        'category': Category.query.get_or_404(category_id),
        'network': Network.query.get_or_404(network_id) if network_id else None,
        'gateway': Gateway.query.get_or_404(gateway_id) if gateway_id != '__none' else None,
    }

    class Form(ProductForm):
        pass

    names = get_category_properties(data['category'])
    add_form_fields(Form, names)

    form = Form(data=data)

    if form.validate_on_submit():
        product = Product()
        product.network = data['network']
        product.gateway = data['gateway']
        product.category = data['category']
        update_product_properties(product, form, names)
        db.session.add(product)
        db.session.commit()
        flash('Create %s successful' % product)
        return redirect(url_for('.product_index'))

    action_url = url_for('.product_new', network_id=network_id, gateway_id=gateway_id, category_id=category_id)
    return render_template('product/new.html', action_url=action_url, form=form, **data)


@bp.route('/products/<int:id>/delete', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def product_delete(id):
    return resource_delete('product', id=id)


@bp.route('/products/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def product_edit(id):
    product = resource_instance('product', id=id)

    class Form(ProductForm):
        pass

    names = get_category_properties(product.category)
    set_product_properties(product, names)
    add_form_fields(Form, names)

    form = Form(obj=product)

    if form.validate_on_submit():
        update_product_properties(product, form, names)
        db.session.commit()
        flash('Update %s successful' % product)
        return redirect(url_for('.product_index'))

    return render_template('product/edit.html',
                           category=product.category,
                           form=form,
                           instance=product,
                           resource='product')


@bp.route('/countries')
@login_required
@roles_accepted('super-admin')
@register_menu(
    bp,
    'countries',
    'Countries',
    visible_when=has_role('super-admin'),
    order=82
)
def country_index():
    return resource_index('country')


@bp.route('/countries/new', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin')
def country_new():
    form = CountryForm()
    return resource_new('country', form)


@bp.route('/countries/<id>/delete', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin')
def country_delete(id):
    return resource_delete('country', id=id)


@bp.route('/countries/<id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin')
def country_edit(id):
    return resource_edit('country', CountryForm, id=id)


@bp.route('/currencies')
@login_required
@roles_accepted('super-admin')
@register_menu(
    bp,
    'currencies',
    'Currencies',
    visible_when=has_role('super-admin'),
    order=84
)
def currency_index():
    return resource_index('currency')


@bp.route('/currencies/new', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def currency_new():
    form = CurrencyForm()
    return resource_new('currency', form)


@bp.route('/currencies/<id>/delete', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def currency_delete(id):
    return resource_delete('currency', id=id)


@bp.route('/currencies/<id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def currency_edit(id):
    return resource_edit('currency', CurrencyForm, id=id)


@bp.route('/cashups')
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
@register_menu(
    bp,
    'cashups',
    'Cashups',
    visible_when=has_admin_role(),
    order=60,
    new_url=lambda: url_for('auth.cashup_new')
)
def cashup_index():
    return resource_index('cashup')


@bp.route('/cashups/new', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def cashup_new():
    if Transaction.query.filter_by(cashup=None).count() == 0 \
            and Adjustment.query.filter_by(cashup=None).count() == 0:
        flash('No new transactions or adjustments since last cashup', 'warning')
        return redirect(redirect_url())

    form = CashupForm(data={'user': current_user})

    gateway_admin = current_user.has_role('gateway-admin')

    if gateway_admin:
        del form.gateway

    if form.validate_on_submit():
        cashup = Cashup()
        cashup.gateway = current_user.gateway if gateway_admin else form.gateway.data
        cashup.user = current_user
        form.populate_obj(cashup)
        db.session.add(cashup)
        db.session.commit()

        for adjustment in cashup.gateway.adjustments \
                .filter(Adjustment.created_at < cashup.created_at, Adjustment.cashup == None):
            cashup.adjustments.append(adjustment)
        for transaction in cashup.gateway.transactions \
                .filter(Transaction.created_at < cashup.created_at, Transaction.cashup == None):
            cashup.transactions.append(transaction)
        db.session.commit()

        flash('Create %s successful' % cashup)
        return redirect(url_for('.cashup_index'))
    return render_template('cashup/new.html', form=form)


@bp.route('/cashups/<id>/delete', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def cashup_delete(id):
    return resource_delete('cashup', id=id)


@bp.route('/cashups/<id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def cashup_show(id):
    return resource_show('cashup', id=id)


@bp.route('/transactions')
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
@register_menu(
    bp,
    'transactions',
    'Transactions',
    visible_when=has_admin_role(),
    order=45
)
def transaction_index():
    return resource_index('transaction', TransactionFilterForm(formdata=request.args))


@bp.route('/transactions/<hash>')
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def transaction_show(hash):
    transaction = Transaction.query.filter_by(hash=hash).first_or_404()
    return render_template('transaction/show.html', transaction=transaction)


@bp.route('/transactions/<hash>/<action>', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def transaction_action(hash, action):
    return resource_action('transaction', action, hash=hash)


@bp.route('/adjustments')
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
@register_menu(
    bp,
    'adjustments',
    'Adjustments',
    visible_when=has_admin_role(),
    order=42,
    new_url=lambda: url_for('auth.adjustment_new')
)
def adjustment_index():
    return resource_index('adjustment')


@bp.route('/adjustments/<hash>')
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def adjustment_show(hash):
    adjustment = Adjustment.query.filter_by(hash=hash).first_or_404()
    return render_template('adjustment/show.html', adjustment=adjustment)


@bp.route('/adjustments/new', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def adjustment_new():
    form = AdjustmentForm()
    if form.validate_on_submit():
        network = form.network.data
        adjustment = Adjustment()
        adjustment.currency = network.currency
        adjustment.user = current_user
        form.populate_obj(adjustment)
        db.session.add(adjustment)
        db.session.commit()
        flash('Create %s successful' % adjustment)
        return redirect(url_for('.adjustment_index'))
    return render_template('adjustment/new.html', form=form, resource='adjustment')


@bp.route('/adjustments/<id>/delete', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def adjustment_delete(id):
    return resource_delete('adjustment', id=id)


@bp.route('/adjustments/<id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def adjustment_edit(id):
    return resource_edit('adjustment', AdjustmentForm, id=id)


@bp.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('favicon.ico')


@bp.route('/uploads/<path:path>')
def uploads(path):
    directory = os.path.join(current_app.instance_path, 'uploads')
    cache_timeout = current_app.get_send_file_max_age(path)
    return send_from_directory(directory, path, cache_timeout=cache_timeout, conditional=True)


@bp.route('/auth-token')
@login_required
def auth_token():
    return current_user.get_auth_token()


@bp.route('/healthcheck')
@auth_token_required
def healthcheck():
    return healthcheck_service.check()


@bp.route('/environment')
@auth_token_required
def environment():
    return environment_dump.dump_environment()


@bp.route('/raise-exception')
@login_required
def raise_exception():
    abort(int(request.args.get('status', 500)))


@bp.route('/')
def home():
    return redirect(url_for('security.login'))

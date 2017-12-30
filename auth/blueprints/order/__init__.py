from auth.forms import FilterForm, instances
from auth.graphs import graphs
from auth.grids import Grid
from auth.models import \
    db, \
    Gateway, \
    Network, \
    Order, \
    OrderItem, \
    Product
from auth.utils import has_admin_role, redirect_url
from auth.views import \
    resource_action, \
    resource_delete, \
    resource_index, \
    resource_instance
from flask import \
    abort, \
    Blueprint, \
    flash, \
    redirect, \
    render_template, \
    request, \
    url_for
from flask_menu import register_menu
from flask_security import \
    current_user, \
    login_required, \
    roles_accepted
from flask_wtf import FlaskForm
from wtforms import fields as f, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectField


order = Blueprint('order', __name__)


def status_choices():
    return [('', 'Select Status')] + \
        [(status, status) for status in graphs['order']['states'].keys()]


class OrderFilterForm(FilterForm):
    network = QuerySelectField('Network',
                               allow_blank=True,
                               query_factory=instances('network'),
                               blank_text='Select Network')
    gateway = QuerySelectField('Gateway',
                               allow_blank=True,
                               query_factory=instances('gateway'),
                               blank_text='Select Gateway')
    user = QuerySelectField('User',
                            allow_blank=True,
                            query_factory=instances('user'),
                            blank_text='Select User')
    status = f.SelectField('Status', default='', choices=status_choices())
    created_from = f.TextField('Created From')
    created_to = f.TextField('Created To')

    def created_from(self, q, k, v):
        return q.filter(Order.created_at >= v)

    def created_to(self, q, k, v):
        return q.filter(Order.created_at < v)


class OrderForm(FlaskForm):
    gateway = f.SelectField('Gateway', default=lambda: current_user.gateway)
    product = QuerySelectField('Product', query_factory=instances('product'))
    quantity = f.IntegerField('Quantity', default=1)
    price = f.DecimalField('Price', [validators.Required()])


class OrderGrid(Grid):
    columns = [
        'id',
        'network_gateway',
        'user'
        'status',
        'total',
        'created_at',
        'actions',
    ]

    def id(self, order):
        return '<a href="%s">%s</a><br/> %s' % \
                (url_for('.order_edit', hash=order.hash), order, order.hash)

    def total(self, order):
        return order.network.currency.render_amount(order.total_amount)


@order.route('/orders')
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
@register_menu(
    order,
    'orders',
    'Orders',
    visible_when=has_admin_role,
    order=36,
    new_url=lambda: url_for('auth.order_new')
)
def order_index():
    return resource_index('order', OrderFilterForm(formdata=request.args))


def _gateway_choices():
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
            networks = [current_user.network]
        else:
            networks = Network.query.all()

        for network in networks:
            for gateway in network.gateways:
                choices.append([
                    gateway.id,
                    '%s - %s' % (network.title,
                                 gateway.title)
                ])

    return choices


@order.route('/orders/new', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def order_new():
    form = OrderForm()

    show_gateway = current_user.has_role('super-admin') or \
        current_user.has_role('network-admin')

    if show_gateway:
        choices = _gateway_choices()

        if choices == []:
            flash('Define a network and gateway first.')
            return redirect(redirect_url())

        form.gateway.choices = choices
    else:
        del form.gateway

    if form.validate_on_submit():
        if show_gateway:
            gateway = Gateway.query.get_or_404(form.gateway.data)
        else:
            gateway = current_user.gateway

        currency = gateway.network.currency

        order = Order()
        order.gateway = gateway
        order.currency = currency
        order.user = current_user

        order_item = OrderItem()
        form.populate_obj(order_item)
        order.items.append(order_item)
        order.calculate_totals()

        db.session.add(order)
        db.session.commit()

        flash('Create %s successful' % order)
        return redirect(url_for('.order_edit', hash=order.hash))

    # TODO This should be a union of global products,
    # then network then gateway
    products = Product.query

    if products.count() == 0:
        abort(404, 'Create a product.')

    prices = dict((p.id, p.price) for p in products.all())
    price = '%.2f' % (list(prices.values())[0])

    return render_template('order/new.html',
                           form=form,
                           price=price,
                           prices=prices)


@order.route('/orders/<hash>', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def order_edit(hash):
    order = resource_instance('order', hash=hash)

    if order.status == 'new':
        form = OrderForm(obj=order)

        show_gateway = current_user.has_role('super-admin') or \
            current_user.has_role('network-admin')

        if show_gateway:
            choices = _gateway_choices()

            if choices == []:
                flash('Define a network and gateway first.')
                return redirect(redirect_url())

            form.gateway.choices = choices
            gateway = Gateway.query.get(form.gateway.data)
        else:
            del form.gateway
            gateway = current_user.gateway

        if form.validate_on_submit():
            order.gateway = gateway

            order_item = OrderItem()
            form.populate_obj(order_item)

            order.items.append(order_item)
            order.calculate_totals()

            db.session.commit()

            flash('Create %s successful' % order)
            return redirect(url_for('.order_edit', hash=order.hash))

        prices = dict((p.id, p.price) for p in Product.query.all())
        price = '%.2f' % (list(prices.values())[0])

        return render_template('order/edit.html',
                               form=form,
                               instance=order,
                               price=price,
                               prices=prices,
                               resource='order')

    return render_template('order/show.html', order=order)


@order.route('/orders/<id>/delete', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def order_delete(id):
    return resource_delete('order', id=id)


@order.route('/order-items/<int:id>/<action>', methods=['GET'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def order_item_action(id, action):
    order_item = OrderItem.query.filter_by(id=id).first_or_404()
    order_item_label = str(order_item)
    order = order_item.order

    if action == 'delete':
        db.session.delete(order_item)
    else:
        abort(403)

    order.calculate_totals()
    db.session.commit()

    flash('%s %s successful' %
          (action[0].upper() + action[1:], order_item_label))
    return redirect(url_for('.order_edit', hash=order.hash))


@order.route('/orders/<hash>/pay/<processor_id>', methods=['GET', 'POST'])
def order_pay(hash, processor_id):
    order = resource_instance('order', hash=hash)
    processor = resource_instance('processor', id=processor_id)
    return processor.pay_order(order)


@order.route('/orders/<hash>/<action>', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def order_action(hash, action):
    return resource_action('order', action, hash=hash)

from __future__ import absolute_import

from auth.models import \
    Adjustment, \
    Cashup, \
    Category, \
    Country, \
    Currency, \
    Gateway, \
    Network, \
    Order, \
    Processor, \
    Product, \
    Transaction, \
    User, \
    Voucher
from collections import defaultdict
from flask_security import current_user


RESOURCE_MODELS = {
    'adjustment': Adjustment,
    'cashup': Cashup,
    'category': Category,
    'country': Country,
    'currency': Currency,
    'gateway': Gateway,
    'network': Network,
    'order': Order,
    'processor': Processor,
    'product': Product,
    'transaction': Transaction,
    'user': User,
    'voucher': Voucher,
}


def resource_query(resource):
    """Generate a filtered query for a resource"""
    model = RESOURCE_MODELS[resource]
    query = model.query

    if current_user.has_role('network-admin') or current_user.has_role('gateway-admin'):
        if model == Network:
            query = query.filter_by(id=current_user.network_id)
        elif model in [Gateway, User]:
            query = query.filter_by(network_id=current_user.network_id)

    if current_user.has_role('network-admin'):
        if model == Voucher:
            query = query.join(Voucher.gateway).join(Gateway.network).filter(Network.id == current_user.network_id)

    if current_user.has_role('gateway-admin'):
        if model == Gateway:
            query = query.filter_by(id=current_user.gateway_id)
        elif model in [User, Voucher]:
            query = query.filter_by(gateway_id=current_user.gateway_id)

    return query


def resource_instance(resource, param, param_name='id'):
    model = RESOURCE_MODELS[resource]
    query = resource_filters[resource](resource_query(resource)).filter(getattr(model, param_name) == param)
    return query.first_or_404()


resource_filters = defaultdict(lambda: lambda query: query)

resource_filters.update({
    'adjustment': lambda query: query.order_by(Adjustment.created_at.desc()),
    'cashup': lambda query: query.order_by(Cashup.created_at.desc()),
    'category': lambda query: query.order_by(Category.sequence),
    'order': lambda query: query.filter(Order.status != 'archived')
                                .order_by(Order.created_at.desc()),
    'product': lambda query: query.order_by(Product.sequence),
    'transaction': lambda query: query.filter(Transaction.status != 'archived')
                                      .order_by(Transaction.created_at.desc()),
    'user': lambda query: query.order_by(User.email),
    'voucher': lambda query: query.filter(Voucher.status != 'archived')
                                  .order_by(Voucher.status, Voucher.created_at.desc()),
})


def resource_instances(resource):
    return resource_filters[resource](resource_query(resource))

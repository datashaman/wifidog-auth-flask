from __future__ import absolute_import

from auth import constants
from auth.models import \
    Adjustment, \
    Cashup, \
    Category, \
    Country, \
    Currency, \
    db, \
    Gateway, \
    Network, \
    Order, \
    Processor, \
    Product, \
    Transaction, \
    User, \
    Voucher
from collections import defaultdict
from flask import abort, flash, redirect, render_template, request, url_for
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

resource_filters = defaultdict(lambda: lambda query: query)

resource_filters.update({
    'adjustment': lambda query: query.order_by(Adjustment.created_at.desc()),
    'cashup': lambda query: query.order_by(Cashup.created_at.desc()),
    'category': lambda query: query.order_by(Category.sequence),
    'order': lambda query: query.filter(Order.status != 'archived'),
    'product': lambda query: query.join(Category)
                                  .order_by(Category.sequence,
                                            Product.sequence),
    'transaction': lambda query: query.filter(Transaction.status != 'archived')
                                      .order_by(Transaction.created_at.desc()),
    'user': lambda query: query.order_by(User.email),
    'voucher': lambda query: query.filter(Voucher.status != 'archived'),
})


def resource_query(resource):
    """
    Generate a filtered query for a resource.
    Avoid using joins in this function, it causes issues.
    """
    model = RESOURCE_MODELS[resource]
    query = model.query

    if current_user.has_role('network-admin') or \
            current_user.has_role('gateway-admin'):
        if model == Network:
            query = query.filter_by(id=current_user.network_id)
        elif model in [Gateway, User]:
            query = query.filter_by(network_id=current_user.network_id)

    if current_user.has_role('network-admin'):
        if model == Voucher:
            gateway_ids = [g.id for g in current_user.network.gateways]
            query = query.filter(Voucher.gateway_id.in_(gateway_ids))

    if current_user.has_role('gateway-admin'):
        if model == Gateway:
            query = query.filter_by(id=current_user.gateway_id)
        elif model in [User, Voucher]:
            query = query.filter_by(gateway_id=current_user.gateway_id)

    return query


def clean_filters(filters):
    clean = {}
    for k, v in filters.items():
        if v != '__None':
            clean[k] = v
    return clean


def resource_instances(resource, grid=None, form=None):
    model = RESOURCE_MODELS[resource]
    query = resource_filters[resource](resource_query(resource))

    if grid is not None:
        sort = grid.current_sort
        if hasattr(grid, 'sort_%s' % sort[0][0]):
            query = getattr(grid, 'sort_%s' % sort[0][0])(query, sort[0][1])
        else:
            for s in sort:
                query = query.order_by(getattr(getattr(model, s[0]), s[1])())

    if form is None:
        return query

    return form.filter_query(query)


def resource_instance(resource, **filters):
    return resource_instances(resource).filter_by(**filters).first_or_404()


def resource_url_for(resource, verb, **kwargs):
    return url_for('%s.%s' % (resource, verb), **kwargs)


def resource_grid(resource, grid=None, filter_form=None):
    """Handle a resource grid request"""
    pagination = resource_instances(resource, grid, filter_form).paginate()
    return render_template('shared/grid.html',
                           filter_form=filter_form,
                           grid=grid,
                           pagination=pagination,
                           resource=resource)


def resource_index(resource, form=None):
    """Handle a resource index request"""
    pagination = resource_instances(resource, None, form).paginate()
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

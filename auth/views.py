"""
Views for the app
"""

from __future__ import absolute_import
from __future__ import division

import os

from auth import constants
from auth.forms import AdjustmentForm

from auth.models import Adjustment, db

from auth.resources import \
        resource_instance, \
        resource_instances, \
        RESOURCE_MODELS
from auth.services import \
        environment_dump, \
        healthcheck as healthcheck_service
from auth.utils import has_role

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


bp = Blueprint('auth', __name__)


def has_admin_role():
    return has_role('super-admin', 'network-admin', 'gateway-admin')


def resource_url_for(resource, verb, **kwargs):
    if resource in [
        'category',
        'country',
        'currency',
        'gateway',
        'network',
        'order',
        'product',
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
    return render_template('adjustment/new.html',
                           form=form,
                           resource='adjustment')


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
    return send_from_directory(directory,
                               path,
                               cache_timeout=cache_timeout,
                               conditional=True)


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

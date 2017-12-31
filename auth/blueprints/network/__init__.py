from auth.models import Network
from auth.resources import \
    resource_delete, \
    resource_edit, \
    resource_index, \
    resource_new
from auth.services import db
from auth.utils import has_role
from flask import Blueprint, flash, redirect, render_template
from flask_menu import register_menu
from flask_security import \
    current_user, \
    login_required, \
    roles_accepted
from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.orm import model_form

network = Blueprint('network', __name__, template_folder='templates')


NetworkForm = model_form(
    Network,
    db.session,
    FlaskForm,
    exclude=[
        'adjustments',
        'categories',
        'created_at',
        'gateways',
        'orders',
        'products',
        'transactions',
        'updated_at',
        'users',
    ],
    exclude_pk=False,
    field_args={
        'ga_tracking_id': {
            'label': 'Google Analytics Tracking ID',
        },
        'id': {
            'label': 'ID',
        },
    }
)


@network.route('/')
@login_required
@roles_accepted('super-admin')
@register_menu(
    network,
    'networks',
    'Networks',
    visible_when=has_role('super-admin'),
    order=85
)
def index():
    return resource_index('network')


@network.route('/new', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin')
def new():
    form = NetworkForm()
    return resource_new('network', form)


@network.route('/<id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin')
def edit(id):
    return resource_edit('network', NetworkForm, id=id)


@network.route('/<id>/delete', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin')
def delete(id):
    return resource_delete('network', id=id)


@network.route('/mine', methods=['GET', 'POST'])
@login_required
@roles_accepted('network-admin')
@register_menu(
    network,
    '.network',
    'My Network',
    visible_when=has_role('network-admin'),
    order=110
)
def mine():
    form = NetworkForm(obj=current_user.network)
    if form.validate_on_submit():
        form.populate_obj(current_user.network)
        db.session.commit()
        flash('Update successful')
        return redirect('/')
    return render_template('network/current.html',
                           form=form,
                           instance=current_user.network)

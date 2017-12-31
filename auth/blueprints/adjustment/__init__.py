from auth.forms import model_form, model_converter
from auth.models import db, Adjustment
from auth.resources import \
    resource_delete, \
    resource_edit, \
    resource_index
from auth.utils import has_admin_role
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_menu import register_menu
from flask_security import \
    current_user, \
    login_required, \
    roles_accepted
from flask_wtf import FlaskForm


adjustment = Blueprint('adjustment', __name__, template_folder='templates')


AdjustmentForm = model_form(
    Adjustment,
    db.session,
    FlaskForm,
    exclude=[
        'created_at',
        'currency',
        'hash',
        'updated_at',
        'user',
    ],
    converter=model_converter
)


@adjustment.route('/')
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
@register_menu(
    adjustment,
    'adjustments',
    'Adjustments',
    visible_when=has_admin_role(),
    order=42,
    new_url=lambda: url_for('adjustment.new')
)
def index():
    return resource_index('adjustment')


@adjustment.route('/<hash>')
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def show(hash):
    adjustment = Adjustment.query.filter_by(hash=hash).first_or_404()
    return render_template('adjustment/show.html', adjustment=adjustment)


@adjustment.route('/new', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def new():
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
        return redirect(url_for('.index'))
    return render_template('adjustment/new.html',
                           form=form,
                           resource='adjustment')


@adjustment.route('/<id>/delete', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def delete(id):
    return resource_delete('adjustment', id=id)


@adjustment.route('/<id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def edit(id):
    return resource_edit('adjustment', AdjustmentForm, id=id)

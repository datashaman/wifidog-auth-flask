from auth.forms import model_form
from auth.models import \
    db, \
    Adjustment, \
    Cashup, \
    Transaction
from auth.resources import \
    resource_delete, \
    resource_index, \
    resource_show
from auth.utils import has_admin_role, redirect_url
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_menu import register_menu
from flask_security import \
    current_user, \
    login_required, \
    roles_accepted
from flask_wtf import FlaskForm


cashup = Blueprint('cashup', __name__, template_folder='templates')


CashupForm = model_form(
    Cashup,
    db.session,
    FlaskForm,
    exclude=[
        'adjustments',
        'created_at',
        'transactions',
        'user',
    ]
)


@cashup.route('/')
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
@register_menu(
    cashup,
    'cashups',
    'Cashups',
    visible_when=has_admin_role,
    order=60,
    new_url=lambda: url_for('cashup.new')
)
def index():
    return resource_index('cashup')


@cashup.route('/new', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def new():
    if Transaction.query.filter_by(cashup=None).count() == 0 \
            and Adjustment.query.filter_by(cashup=None).count() == 0:
        flash('No new transactions or adjustments since last cashup',
              'warning')
        return redirect(redirect_url())

    form = CashupForm(data={'user': current_user})

    gateway_admin = current_user.has_role('gateway-admin')

    if gateway_admin:
        del form.gateway

    if form.validate_on_submit():
        cashup = Cashup()
        cashup.gateway = current_user.gateway \
            if gateway_admin else form.gateway.data
        cashup.user = current_user
        form.populate_obj(cashup)
        db.session.add(cashup)
        db.session.commit()

        for adjustment in cashup.gateway.adjustments \
                .filter(Adjustment.created_at < cashup.created_at,
                        Adjustment.cashup is None):
            cashup.adjustments.append(adjustment)
        for transaction in cashup.gateway.transactions \
                .filter(Transaction.created_at < cashup.created_at,
                        Transaction.cashup is None):
            cashup.transactions.append(transaction)
        db.session.commit()

        flash('Create %s successful' % cashup)
        return redirect(url_for('.index'))
    return render_template('cashup/new.html', form=form)


@cashup.route('/<id>/delete', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def delete(id):
    return resource_delete('cashup', id=id)


@cashup.route('/<id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def show(id):
    return resource_show('cashup', id=id)

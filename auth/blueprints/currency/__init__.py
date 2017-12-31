from auth.forms import model_form
from auth.models import Currency
from auth.resources import \
    resource_delete, \
    resource_edit, \
    resource_index, \
    resource_new
from auth.services import db
from auth.utils import has_role
from flask import Blueprint
from flask_menu import register_menu
from flask_security import \
    login_required, \
    roles_accepted
from flask_wtf import FlaskForm


currency = Blueprint('currency', __name__, template_folder='templates')


CurrencyForm = model_form(
    Currency,
    db.session,
    FlaskForm,
    exclude=[
        'adjustments',
        'created_at',
        'networks',
        'orders',
        'products',
        'transactions',
        'updated_at',
    ],
    exclude_pk=False,
    field_args={
        'id': {
            'label': 'ID',
        },
    }
)


@currency.route('/')
@login_required
@roles_accepted('super-admin')
@register_menu(
    currency,
    'currencies',
    'Currencies',
    visible_when=has_role('super-admin'),
    order=84
)
def index():
    return resource_index('currency')


@currency.route('/new', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def new():
    form = CurrencyForm()
    return resource_new('currency', form)


@currency.route('/<id>/delete', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def delete(id):
    return resource_delete('currency', id=id)


@currency.route('/<id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def edit(id):
    return resource_edit('currency', CurrencyForm, id=id)

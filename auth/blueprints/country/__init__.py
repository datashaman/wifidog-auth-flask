from auth.forms import model_form
from auth.models import Country
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


country = Blueprint('country', __name__, template_folder='templates')


CountryForm = model_form(
    Country,
    db.session,
    FlaskForm,
    exclude=[
        'created_at',
        'gateways',
        'updated_at',
        'vat_rates',
    ],
    exclude_pk=False,
    field_args={
        'id': {
            'label': 'ID',
        },
    }
)


@country.route('/')
@login_required
@roles_accepted('super-admin')
@register_menu(
    country,
    'countries',
    'Countries',
    visible_when=has_role('super-admin'),
    order=82
)
def index():
    return resource_index('country')


@country.route('/new', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin')
def new():
    form = CountryForm()
    return resource_new('country', form)


@country.route('/<id>/delete', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin')
def delete(id):
    return resource_delete('country', id=id)


@country.route('/<id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin')
def edit(id):
    return resource_edit('country', CountryForm, id=id)

from auth.forms import instances, model_converter
from auth.models import db, Category
from auth.utils import has_admin_role, redirect_url
from auth.views import \
    resource_delete, \
    resource_edit, \
    resource_index, \
    resource_instance, \
    resource_new
from flask import \
    Blueprint, \
    redirect, \
    request
from flask_menu import register_menu
from flask_security import \
    current_user, \
    login_required, \
    roles_accepted
from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.orm import model_form


category = Blueprint('category', __name__, template_folder='templates')


CategoryForm = model_form(
    Category,
    db.session,
    FlaskForm,
    exclude=[
        'children',
        'created_at',
        'products',
        'read_only',
        'status',
        'sub_categories',
        'updated_at',
    ],
    field_args={
        'gateway': {
            'default': lambda: current_user.gateway,
            'query_factory': instances('gateway'),
        },
        'network': {
            'default': lambda: current_user.network,
            'query_factory': instances('network'),
        }
    },
    converter=model_converter
)


@category.route('/')
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
@register_menu(
    category,
    'categories',
    'Categories',
    visible_when=has_admin_role(),
    order=70
)
def index():
    return resource_index('category')


@category.route('/sort', methods=['POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def sort():
    content = request.get_json()
    for category_id, sequence in content['sequences'].items():
        category = Category.query.get_or_404(category_id)
        category.sequence = sequence
        db.session.commit()
    return 'OK'


@category.route('/new', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def new():
    form = CategoryForm()
    return resource_new('category', form)


@category.route('/<code>/delete', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def delete(code):
    return resource_delete('category', code=code)


@category.route('/<code>', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def edit(code):
    category = resource_instance('category', code=code)
    if category.read_only:
        return redirect(redirect_url())
    return resource_edit('category', CategoryForm, code=code)

from auth.forms import instances, model_converter
from auth.models import \
    Gateway, \
    Network, \
    Product
from auth.resources import \
    resource_delete, \
    resource_index, \
    resource_instance
from auth.services import db
from auth.utils import has_admin_role
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
from wtforms.ext.sqlalchemy.orm import model_form


product = Blueprint('product', __name__, template_folder='templates')


ProductForm = model_form(
    Product,
    db.session,
    FlaskForm,
    exclude=[
        'created_at',
        'gateway',
        'network',
        'order_items',
        'updated_at',
    ],
    converter=model_converter
)


class SelectNetworkGatewayForm(FlaskForm):
    network = QuerySelectField('Network', default=lambda: current_user.network, query_factory=instances('network'))
    gateway = QuerySelectField('Gateway', allow_blank=True, default=lambda: current_user.gateway, query_factory=instances('gateway'))


@product.route('/')
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
@register_menu(
    product,
    'products',
    'Products',
    visible_when=has_admin_role,
    order=80
)
def index():
    return resource_index('product')


@product.route('/sort', methods=['POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def sort():
    content = request.get_json()
    for product_id, sequence in content['sequences'].items():
        product = Product.query.get_or_404(product_id)
        product.sequence = sequence
        db.session.commit()
    return 'OK'


def get_category_properties(category):
    names = category.properties
    return names.split('\n') if names else []


def set_product_properties(product, names):
    if product.properties:
        lines = product.properties.split('\n')
        for line in lines:
            (k, v) = line.split('=')
            if k in names:
                setattr(product, k, v)


def add_form_fields(form, names):
    for name in names:
        setattr(form,
                name,
                f.StringField(name[0].upper() + name[1:],
                              validators=[
                                  validators.InputRequired(),
                              ],
                              _name=name))


def update_product_properties(product, form, names):
    form.populate_obj(product)
    if names:
        values = {}
        for name in names:
            values[name] = getattr(form, name).data
        product.properties = '\n'.join('%s=%s' % (k, v) for k, v in values.items())


@product.route('/new/<network_id>/<gateway_id>/<category_id>', methods=['GET', 'POST'])
@product.route('/new/<network_id>/<gateway_id>', methods=['GET', 'POST'])
@product.route('/new/<network_id>', methods=['GET', 'POST'])
@product.route('/new', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def new(network_id=None, gateway_id=None, category_id=None):
    if network_id is None and gateway_id is None:
        if current_user.has_role('gateway-admin'):
            url = url_for('.new',
                          network_id=current_user.network.id,
                          gateway_id=current_user.gateway.id)
            return redirect(url)

        form = SelectNetworkGatewayForm()

        if form.validate_on_submit():
            gateway_id = form.gateway.data.id if form.gateway.data else '__none'
            url = url_for('.new',
                          network_id=form.network.data.id,
                          gateway_id=gateway_id)
            return redirect(url)
        return render_template('shared/select-network-gateway.html',
                               action_url=url_for('.new'),
                               form=form)

    if current_user.has_role('gateway-admin'):
        if network_id != current_user.network.id or gateway_id != current_user.gateway.id:
            abort(403)

    if current_user.has_role('network-admin'):
        if network_id != current_user.network.id:
            abort(403)

        if gateway_id != '__none' and current_user.network.gateways.filter_by(id=gateway_id).count() == 0:
            abort(403)

    if category_id is None:
        choices = Category.query.filter(Category.network == None, Category.gateway == None).all()

        if network_id:
            choices += Category.query.filter(Category.network_id == network_id,
                                             Category.gateway_id == None).all()

        if network_id and gateway_id:
            choices += Category.query.filter(Category.network_id == network_id,
                                             Category.gateway_id == gateway_id).all()

        form = SelectCategoryForm()

        if form.validate_on_submit():
            gateway_id = '__none' if gateway_id is None else gateway_id
            url = url_for('.new', network_id=network_id, gateway_id=gateway_id, category_id=form.category.data.id)
            return redirect(url)

        return render_template('shared/select-category.html',
                               action_url=url_for('.new', network_id=network_id, gateway_id=gateway_id),
                               form=form)

    data = {
        'category': Category.query.get_or_404(category_id),
        'network': Network.query.get_or_404(network_id) if network_id else None,
        'gateway': Gateway.query.get_or_404(gateway_id) if gateway_id != '__none' else None,
    }

    class Form(ProductForm):
        pass

    names = get_category_properties(data['category'])
    add_form_fields(Form, names)

    form = Form(data=data)

    if form.validate_on_submit():
        product = Product()
        product.network = data['network']
        product.gateway = data['gateway']
        product.category = data['category']
        update_product_properties(product, form, names)
        db.session.add(product)
        db.session.commit()
        flash('Create %s successful' % product)
        return redirect(url_for('.index'))

    action_url = url_for('.new', network_id=network_id, gateway_id=gateway_id, category_id=category_id)
    return render_template('product/new.html', action_url=action_url, form=form, **data)


@product.route('/<int:id>/delete', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def delete(id):
    return resource_delete('product', id=id)


@product.route('/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def edit(id):
    product = resource_instance('product', id=id)

    class Form(ProductForm):
        pass

    names = get_category_properties(product.category)
    set_product_properties(product, names)
    add_form_fields(Form, names)

    form = Form(obj=product)

    if form.validate_on_submit():
        update_product_properties(product, form, names)
        db.session.commit()
        flash('Update %s successful' % product)
        return redirect(url_for('.index'))

    return render_template('product/edit.html',
                           category=product.category,
                           form=form,
                           instance=product,
                           resource='product')

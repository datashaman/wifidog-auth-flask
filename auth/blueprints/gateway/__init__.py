from auth.forms import converts, instances, ModelConverter
from auth.models import db, Gateway, GatewayType
from auth.resources import \
    resource_delete, \
    resource_index
from auth.services import logos
from auth.utils import has_role
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_menu import register_menu
from flask_security import \
    current_user, \
    login_required, \
    roles_accepted
from flask_wtf import FlaskForm
from PIL import Image
from wtforms import fields as f
from wtforms.ext.sqlalchemy.orm import model_form

gateway = Blueprint('gateway', __name__, template_folder='templates')


class GatewayConverter(ModelConverter):
    @converts('String', 'Unicode')
    def conv_String(self, field_args, **extra):
        if extra['column'].name == 'logo':
            return f.FileField(**field_args)
        else:
            return ModelConverter.conv_String(self, field_args, **extra)


GatewayForm = model_form(
    Gateway,
    db.session,
    FlaskForm,
    exclude=[
        'adjustments',
        'auths',
        'cashups',
        'created_at',
        'categories',
        'last_ping_ip',
        'last_ping_at',
        'last_ping_user_agent',
        'last_ping_sys_uptime',
        'last_ping_wifidog_uptime',
        'last_ping_sys_memfree',
        'last_ping_sys_load',
        'orders',
        'products',
        'transactions',
        'updated_at',
        'users',
        'vouchers',
    ],
    exclude_pk=False,
    field_args={
        'id': {
            'label': 'ID',
        },
        'gateway_type': {
            'default': lambda: GatewayType.query.get('cafe'),
        },
        'logo': {
            'description': 'Images only, resampled down to 300 x 300 pixels.',
        },
        'network': {
            'default': lambda: current_user.network,
            'query_factory': instances('network'),
        },
        'url_facebook': {
            'label': 'Facebook Page',
        },
        'url_home': {
            'label': 'Home Page',
        },
        'url_map': {
            'label': 'Map URL',
        },
        'vat_number': {
            'label': 'VAT Number',
        },
    },
    converter=GatewayConverter()
)


@gateway.route('/')
@login_required
@roles_accepted('super-admin', 'network-admin')
@register_menu(
    gateway,
    'gateways',
    'Gateways',
    visible_when=has_role('super-admin', 'network-admin'),
    order=87
)
def index():
    return resource_index('gateway')


def handle_logo(form):
    if request.files['logo']:
        filename = form.logo.data = \
            logos.save(request.files['logo'], name='%s.' % form.id.data)
        im = Image.open(logos.path(filename))
        im.thumbnail((300, 300), Image.ANTIALIAS)
        im.save(logos.path(filename))
    else:
        del form.logo


@gateway.route('/new', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin')
def new():
    form = GatewayForm()
    if form.validate_on_submit():
        handle_logo(form)
        gateway = Gateway()
        form.populate_obj(gateway)
        db.session.add(gateway)
        db.session.commit()
        flash('Create %s successful' % gateway)
        return redirect(url_for('.index'))
    return render_template('gateway/new.html', form=form)


def _edit(gateway, page_title, action_url):
    form = GatewayForm(obj=gateway)
    if form.validate_on_submit():
        handle_logo(form)
        form.populate_obj(gateway)
        db.session.commit()
        flash('Update %s successful' % gateway)
        return redirect(url_for('auth.home'))
    return render_template('gateway/edit.html',
                           action_url=action_url,
                           form=form,
                           instance=gateway,
                           logos=logos,
                           page_title=page_title)


@gateway.route('/<id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin')
def edit(id):
    gateway = Gateway.query.filter_by(id=id).first_or_404()
    return _edit(
        gateway,
        'Edit Gateway',
        url_for('.edit', id=id)
    )


@gateway.route('/<id>/delete', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin')
def delete(id):
    return resource_delete('gateway', id=id)


@gateway.route('/mine', methods=['GET', 'POST'])
@login_required
@roles_accepted('gateway-admin')
@register_menu(
    gateway,
    '.gateway',
    'My Gateway',
    visible_when=has_role('gateway-admin'),
    order=120
)
def mine():
    gateway = current_user.gateway
    return _edit(
        gateway,
        'My Gateway',
        url_for('.mine')
    )

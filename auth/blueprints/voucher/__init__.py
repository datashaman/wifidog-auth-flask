from auth.models import Network, Voucher
from auth.resources import resource_action, resource_index
from auth.services import db
from auth.utils import has_admin_role, redirect_url
from flask import \
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


voucher = Blueprint('voucher', __name__, template_folder='templates')


def default_megabytes():
    if current_user.gateway is not None:
        return current_user.gateway.default_megabytes


def default_minutes():
    if current_user.gateway is not None:
        return current_user.gateway.default_minutes


class NewVoucherForm(FlaskForm):
    gateway_id = f.SelectField('Gateway')
    minutes = f.IntegerField('Minutes', [validators.InputRequired(), validators.NumberRange(min=0)], default=default_minutes)
    megabytes = f.IntegerField('Megabytes', [validators.Optional(), validators.NumberRange(min=0)], default=default_megabytes)


@voucher.route('/')
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
@register_menu(
    voucher,
    '.vouchers',
    'Vouchers',
    visible_when=has_admin_role,
    order=20,
    new_url=lambda: url_for('voucher.new')
)
def index():
    return resource_index('voucher')


@voucher.route('/new', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def new():
    form = NewVoucherForm()
    choices = []
    defaults = {}

    if current_user.has_role('gateway-admin'):
        choices = [
            [
                current_user.gateway_id,
                '%s - %s' % (current_user.gateway.network.title,
                             current_user.gateway.title)
            ]
        ]
        defaults[current_user.gateway_id] = {
            'minutes': current_user.gateway.default_minutes,
            'megabytes': current_user.gateway.default_megabytes,
        }
    else:
        if current_user.has_role('network-admin'):
            networks = [current_user.network]
        else:
            networks = Network.query.all()

        for network in networks:
            for gateway in network.gateways:
                choices.append([
                    gateway.id,
                    '%s - %s' % (network.title,
                                 gateway.title)
                ])
                defaults[gateway.id] = {
                    'minutes': gateway.default_minutes,
                    'megabytes': gateway.default_megabytes,
                }

    if choices == []:
        flash('Define a network and gateway first.')
        return redirect(redirect_url())

    form.gateway_id.choices = choices

    item = defaults[choices[0][0]]

    if request.method == 'GET':
        form.minutes.data = item['minutes']
        form.megabytes.data = item['megabytes']

    if form.validate_on_submit():
        voucher = Voucher()
        form.populate_obj(voucher)
        db.session.add(voucher)
        db.session.commit()

        return redirect(url_for('.new', code=voucher.code))

    return render_template('voucher/new.html', form=form, defaults=defaults)


@voucher.route('/<int:id>/<action>', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def action(id, action):
    return resource_action('voucher', action, id=id)

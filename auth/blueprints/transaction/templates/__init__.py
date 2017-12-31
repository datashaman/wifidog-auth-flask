from auth.forms import FilterForm, instances
from auth.graphs import graphs
from auth.models import Transaction
from auth.utils import has_admin_role
from auth.views import resource_action, resource_index
from flask import Blueprint, render_template, request
from flask_menu import register_menu
from flask_security import login_required, roles_accepted
from wtforms import fields as f
from wtforms.ext.sqlalchemy.fields import QuerySelectField


transaction = Blueprint('transaction', __name__, template_folder='templates')


class TransactionFilterForm(FilterForm):
    network = QuerySelectField('Network', allow_blank=True, query_factory=instances('network'), blank_text='Select Network')
    gateway = QuerySelectField('Gateway', allow_blank=True, query_factory=instances('gateway'), blank_text='Select Gateway')
    user = QuerySelectField('User', allow_blank=True, query_factory=instances('user'), blank_text='Select User')
    status = f.SelectField('Status', default='', choices=[('', 'Select Status')] + [(status, status) for status in graphs['order']['states'].keys()])
    created_from = f.StringField('Created From')
    created_to = f.StringField('Created To')

    def filter_created_from(self, q, k, v):
        return q.filter(Transaction.created_at >= v)

    def filter_created_to(self, q, k, v):
        return q.filter(Transaction.created_at < v)


@transaction.route('/')
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
@register_menu(
    transaction,
    'transactions',
    'Transactions',
    visible_when=has_admin_role(),
    order=45
)
def index():
    return resource_index('transaction',
                          TransactionFilterForm(formdata=request.args))


@transaction.route('/<hash>')
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def show(hash):
    transaction = Transaction.query.filter_by(hash=hash).first_or_404()
    return render_template('transaction/show.html', transaction=transaction)


@transaction.route('/<hash>/<action>', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def action(hash, action):
    return resource_action('transaction', action, hash=hash)

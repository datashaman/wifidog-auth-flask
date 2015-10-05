import flask

from app import db
from app.utils import is_logged_in
from flask.ext.security import login_required, roles_required
from flask.ext.menu import register_menu

from models import Voucher, VoucherSchema

bp = flask.Blueprint('vouchers', __name__, url_prefix='/vouchers', template_folder='templates', static_folder='static')

@bp.route('/')
@login_required
@roles_required('admin')
@register_menu(bp, '.vouchers', 'Vouchers', visible_when=is_logged_in)
def index():
    schema = VoucherSchema(many=True)
    vouchers = schema.dump(Voucher.query.all()).data
    return flask.render_template('vouchers/index.html', vouchers=vouchers)

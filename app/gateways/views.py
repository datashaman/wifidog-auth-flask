import flask

from app.utils import is_logged_in, has_a_role
from flask.ext.menu import register_menu
from flask.ext.security import login_required, roles_accepted

bp = flask.Blueprint('gateways', __name__, url_prefix='/gateways', template_folder='templates', static_folder='static')

@bp.route('/')
@login_required
@roles_accepted('super-admin', 'network-admin')
@register_menu(bp, '.gateways', 'Gateways', visible_when=has_a_role('super-admin', 'network-admin'))
def index():
    return flask.render_template('gateways/index.html')

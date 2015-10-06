import flask

from app import db
from app.utils import is_logged_in, has_a_role
from flask.ext.menu import register_menu
from flask.ext.security import login_required, roles_required, roles_accepted

from app.models import User, UserSchema

bp = flask.Blueprint('users', __name__, url_prefix='/users', template_folder='templates', static_folder='static')

@bp.route('/')
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
@register_menu(bp, '.users', 'Users', visible_when=has_a_role('super-admin', 'network-admin', 'gateway-admin'))
def index():
    return flask.render_template('users/index.html')

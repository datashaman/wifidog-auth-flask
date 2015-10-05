import flask

from app.utils import is_logged_in
from flask.ext.menu import register_menu
from flask.ext.security import login_required, roles_required

from models import Gateway, GatewaySchema

bp = flask.Blueprint('gateways', __name__, url_prefix='/gateways', template_folder='templates', static_folder='static')

@bp.route('/')
@login_required
@roles_required('admin')
@register_menu(bp, '.gateways', 'Gateways', visible_when=is_logged_in)
def index():
    schema = GatewaySchema(many=True)
    gateways = schema.dump(Gateway.query.all()).data
    return flask.render_template('gateways/index.html', gateways=gateways)

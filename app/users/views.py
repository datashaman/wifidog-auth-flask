import flask

from app import db
from app.utils import is_logged_in
from flask.ext.menu import register_menu
from flask.ext.security import login_required, roles_required

from models import User, UserSchema

bp = flask.Blueprint('users', __name__, url_prefix='/users', template_folder='templates', static_folder='static')

@bp.route('/')
@login_required
@roles_required('admin')
@register_menu(bp, '.users', 'Users', visible_when=is_logged_in)
def index():
    schema = UserSchema(many=True)
    users = schema.dump(User.query.all()).data
    return flask.render_template('users/index.html', users=users)

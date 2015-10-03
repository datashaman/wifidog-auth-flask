import datetime
import flask
import json

from app import app, db, api_manager
from app.utils import is_logged_in
from flask.ext.login import LoginManager, login_user, logout_user, login_required, AnonymousUserMixin
from flask.ext.menu import register_menu
from flask.ext.script import prompt, prompt_pass

import manager
from forms import LoginForm

from models import User, UserSchema, datastore

api_manager.create_api(User, methods=[ 'GET', 'POST', 'DELETE' ])

def ret(thing):
    def func(self):
        return thing
    return func

AnonymousUserMixin.id = property(ret(None))
AnonymousUserMixin.roles = property(ret([]))

bp = flask.Blueprint('users', __name__, url_prefix='/users', template_folder='templates', static_folder='static')

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(id)

@bp.route('/')
@login_required
@register_menu(bp, '.users', 'Users', visible_when=is_logged_in)
def index():
    schema = UserSchema(many=True)
    users = schema.dump(User.query.all()).data

    if flask.request.is_xhr:
        return flask.jsonify(users=users)
    else:
        return flask.render_template('users/index.html', users=users)

@bp.route('/', methods=[ 'POST' ])
@login_required
def users_create():
    datastore.create_user(email=flask.request.form['id'], password=flask.request.form['password'])
    db.session.commit()
    return ('', 200)

@bp.route('/', methods=[ 'DELETE' ])
@login_required
def users_remove():
    User.query.delete()
    db.session.commit()
    return ('', 200)

@bp.route('/<id>', methods=[ 'DELETE' ])
@login_required
def user_remove(id):
    User.query.filter_by(id=id).delete()
    db.session.commit()
    return('', 200)

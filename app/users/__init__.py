import datetime
import flask
import json

from app import app, db, manager
from app.utils import is_logged_in, is_logged_out
from flask.ext.bcrypt import Bcrypt
from flask.ext.login import LoginManager, login_user, logout_user, UserMixin, login_required
from flask.ext.menu import register_menu
from flask.ext.script import prompt, prompt_pass
from marshmallow import Schema, fields
from wtforms import Form, PasswordField, TextField, HiddenField, validators

bp = flask.Blueprint('users', __name__, url_prefix='/users', template_folder='templates', static_folder='static')

login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.init_app(app)

bcrypt = Bcrypt(app)

def next_value():
    return flask.request.args.get('next')

class LoginForm(Form):
    id = TextField('User ID', [ validators.InputRequired() ])
    password = PasswordField('Password', [ validators.InputRequired() ])
    next = HiddenField(default=next_value)

    def validate_id(self, field):
        user = User.query.get(field.data)

        if user is None:
            raise validators.ValidationError('User does not exist')

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __init__(self, id, password):
        self.id = id
        self.password = User.generate_password_hash(password)

    def __repr__(self):
        return '<User %r>' % self.id

    def to_dict(self):
        return { c.name: getattr(self, c.name) for c in self.__table__.columns }

    def check_password_hash(self, password):
        return bcrypt.check_password_hash(self.password, password)

    @staticmethod
    def generate_password_hash(password):
        return bcrypt.generate_password_hash(password)

@login_manager.user_loader
def load_user(id):
    return User.query.get(id)

class UserSchema(Schema):
    id = fields.Str()
    password = fields.Str()
    created_at = fields.DateTime()

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

def user_menu(*args, **kwargs):
    print args, kwargs

    return [
            { 'url': '/', 'text': 'blah' }
    ]

@bp.route('/login', methods=[ 'GET', 'POST' ])
def login():
    form = LoginForm(flask.request.form)

    if flask.request.method == 'POST' and form.validate():
        user = User.query.get(form.id.data)

        if user is None:
            flask.flash('Invalid Credentials', 'warning')
        else:
            if user.check_password_hash(form.password.data):
                login_user(user)
                flask.flash('You logged in', 'success')
                return flask.redirect(form.next.data or flask.url_for('home'))
            else:
                flask.flash('Invalid Credentials', 'warning')

    return flask.render_template('users/login.html', form=form)

@bp.route('/logout')
@login_required
@register_menu(bp, '.logout', 'Logout', order=99, visible_when=is_logged_in)
def logout():
    logout_user()
    flask.flash('You logged out', 'success')
    return flask.redirect(flask.url_for('home'))

@bp.route('/', methods=[ 'POST' ])
def users_create():
    user = User(flask.request.form['id'], flask.request.form['password'])
    db.session.add(user)
    db.session.commit()
    return ('', 200)

@bp.route('/', methods=[ 'DELETE' ])
def users_remove():
    User.query.delete()
    db.session.commit()
    return ('', 200)

@bp.route('/<id>', methods=[ 'DELETE' ])
def user_remove(id):
    User.query.filter_by(id=id).delete()
    db.session.commit()
    return('', 200)

@manager.command
def create_user():
    id = prompt('User ID')
    password = prompt_pass('Password')
    confirmation = prompt_pass('Confirm Password')

    if password == confirmation:
        user = User(id, password)

        db.session.add(user)
        db.session.commit()

        print 'User created'
    else:
        print "Passwords don't match"

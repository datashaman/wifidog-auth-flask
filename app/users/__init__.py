import datetime
import flask
import json

from app import app, db, manager
from app.utils import is_logged_in, is_logged_out
from flask.ext.bcrypt import Bcrypt
from flask.ext.login import LoginManager, login_user, logout_user, login_required
from flask.ext.menu import register_menu
from flask.ext.script import prompt, prompt_pass
from flask.ext.security import UserMixin, RoleMixin, SQLAlchemyUserDatastore, Security
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
    email = TextField('Email', [ validators.InputRequired() ])
    password = PasswordField('Password', [ validators.InputRequired() ])
    next = HiddenField(default=next_value)

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()

        if user is None:
            raise validators.ValidationError('User does not exist')

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True)
    confirmed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return '<User %r>' % self.email

    def to_dict(self):
        return { c.name: getattr(self, c.name) for c in self.__table__.columns }

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

@login_manager.user_loader
def load_user(id):
    return User.query.get(id)

class UserSchema(Schema):
    id = fields.Int()
    email = fields.Str()
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

# @bp.route('/login', methods=[ 'GET', 'POST' ])
# def login():
#     form = LoginForm(flask.request.form)
# 
#     if flask.request.method == 'POST' and form.validate():
#         user = User.query.filter_by(email=form.email.data).first()
# 
#         if user is None:
#             flask.flash('Invalid Credentials', 'warning')
#         else:
#             if user.check_password_hash(form.password.data):
#                 login_user(user)
#                 flask.flash('You logged in', 'success')
#                 return flask.redirect(form.next.data or flask.url_for('home'))
#             else:
#                 flask.flash('Invalid Credentials', 'warning')
# 
#     return flask.render_template('users/login.html', form=form)
#
#@bp.route('/logout')
#@login_required
#@register_menu(bp, '.logout', 'Logout', order=99, visible_when=is_logged_in)
#def logout():
#    logout_user()
#    flask.flash('You logged out', 'success')
#    return flask.redirect(flask.url_for('home'))
#
@bp.route('/', methods=[ 'POST' ])
def users_create():
    user_datastore.create_user(email=flask.request.form['id'], password=flask.request.form['password'])
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
def create_admin():
    email = prompt('Email')
    password = prompt_pass('Password')
    confirmation = prompt_pass('Confirm Password')

    if password == confirmation:
        user = user_datastore.create_user(email=email, password=password)
        admin = Role.query.filter_by(name='admin').first()
        user.roles.append(admin)
        db.session.commit()

        print 'User created'
    else:
        print "Passwords don't match"

@manager.command
def seed_roles():
    admin = Role()
    admin.name = 'admin'
    admin.description = 'Admin user'
    db.session.add(admin)
    db.session.commit()

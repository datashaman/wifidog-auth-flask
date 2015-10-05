import datetime

from app import app, db, login_manager, api_manager
from app.gateways import Gateway
from flask.ext.restless import ProcessingException
from flask.ext.security import UserMixin, RoleMixin, SQLAlchemyUserDatastore, Security, current_user
from marshmallow import Schema, fields

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('roles.id'))
)

class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    network_id = db.Column(db.Unicode, db.ForeignKey('networks.id'))
    gateway_id = db.Column(db.Unicode, db.ForeignKey('gateways.id'))

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

@login_manager.user_loader
def load_user(id):
    return User.query.get(id)

datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, datastore)

class UserSchema(Schema):
    id = fields.Int()
    email = fields.Str()
    password = fields.Str()
    network_id = fields.Str()
    gateway_id = fields.Str()
    created_at = fields.DateTime()

    def make_object(self, data):
        return User(**data)

def preprocess_many(search_params=None, **kwargs):
    if search_params is None:
        search_params = {}

    if 'filters' not in search_params:
        search_params['filters'] = []

    if current_user.has_role('network-admin'):
        search_params['filters'].append(dict(name='network_id', op='eq', val=current_user.network_id))

    if current_user.has_role('gateway-admin'):
        search_params['filters'].append(dict(name='network_id', op='eq', val=current_user.network_id))
        search_params['filters'].append(dict(name='gateway_id', op='eq', val=current_user.gateway_id))

def preprocess_single(instance_id=None, **kwargs):
    if instance_id is None:
        return

    if current_user.has_role('super-admin'):
        return

    user = User.query.get(instance_id)

    if (current_user.has_role('network-admin')
            and user.network_id == current_user.network_id):
        return

    if (current_user.has_role('gateway-admin')
            and current_user.network_id == user.network_id
            and current_user.gateway_id == user.gateway_id):
        return

    raise ProcessingException(description='Not Authorized', code=401)

api_manager.create_api(User,
        collection_name='users',
        methods=[ 'GET', 'POST', 'DELETE' ],
        allow_delete_many=True,
        preprocessors=dict(
            GET_SINGLE=[preprocess_single],
            GET_MANY=[preprocess_many],
            POST=[preprocess_single],
            DELETE_SINGLE=[preprocess_single],
        ))

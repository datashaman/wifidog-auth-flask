import datetime

from app import app, db, login_manager, api
from app.gateways import Gateway
from flask.ext.principal import Principal, Identity, UserNeed, AnonymousIdentity, identity_loaded, RoleNeed
from flask.ext.potion.contrib.principals import PrincipalResource
from flask.ext.security import Security, UserMixin, RoleMixin, current_user, SQLAlchemyUserDatastore

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

@login_manager.request_loader
def load_user_from_request(request):
    if request.authorization:
        username, password = request.authorization.username, request.authorization.password
        user = User.query.filter_by(email=username).first()

        if user is not None and verify_and_update_password(password, user):
            return user

@login_manager.user_loader
def load_user(id):
    return User.query.get(id)

datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, datastore)
principals = Principal(app)

@principals.identity_loader
def read_identity_from_flask_login():
    if current_user.is_authenticated():
        return Identity(current_user.id)
    return AnonymousIdentity()

@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    if not isinstance(identity, AnonymousIdentity):
        identity.provides.add(UserNeed(identity.id))

        for role in current_user.roles:
            identity.provides.add(RoleNeed(role.name))

admin_roles = [ 'super-admin', 'network-admin', 'gateway-admin' ]

class UserResource(PrincipalResource):
    class Meta:
        model = User
        include_id = True
        permissions = {
            'read': admin_roles,
            'create': admin_roles,
            'update': admin_roles,
            'delete': admin_roles,
        }
        read_only_fields = [ 'created_at' ]

api.add_resource(UserResource)

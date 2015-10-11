import flask

app = flask.Flask(__name__)
app.config.from_object('config')

from app.models import User, Role
from app.resources import GatewayResource, NetworkResource, UserResource, VoucherResource
from app.services import menu, db, manager, api, security, principals, logos
from flask.ext.login import current_user
from flask.ext.potion.contrib.principals.needs import HybridRelationshipNeed
from flask.ext.principal import Identity, UserNeed, AnonymousIdentity, identity_loaded, RoleNeed
from flask.ext.security import SQLAlchemyUserDatastore
from flask.ext.uploads import configure_uploads

import views

menu.init_app(app)
db.init_app(app)

with app.app_context():
    db.create_all()

    api.add_resource(UserResource)
    api.add_resource(VoucherResource)
    api.add_resource(GatewayResource)
    api.add_resource(NetworkResource)

    configure_uploads(app, logos)

manager.app = app
api.init_app(app)
principals.init_app(app)

datastore = SQLAlchemyUserDatastore(db, User, Role)
security.init_app(app, datastore)

@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    if not isinstance(identity, AnonymousIdentity):
        identity.provides.add(UserNeed(identity.id))

        for role in current_user.roles:
            identity.provides.add(RoleNeed(role.name))

@principals.identity_loader
def read_identity_from_flask_login():
    if current_user.is_authenticated():
        return Identity(current_user.id)
    return AnonymousIdentity()

@app.route('/')
def home():
    return flask.redirect(flask.url_for('security.login'))

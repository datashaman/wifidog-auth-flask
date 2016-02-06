import datetime
import flask
import uuid

from app.admin import VoucherAdmin
from app.models import User, Role, db, users
from app.resources import api, GatewayResource, NetworkResource, UserResource, VoucherResource, logos
from app.services import influx_db, menu, security
from app.signals import init_signals
from app.views import bp

from flask.ext.login import current_user, LoginManager
from flask.ext.uploads import configure_uploads
from flask.ext.potion.contrib.principals.needs import HybridRelationshipNeed
from flask.ext.principal import Identity, UserNeed, AnonymousIdentity, identity_loaded, RoleNeed, Principal

def create_app(config=None):
    app = flask.Flask(__name__)

    app.config.from_object('config')

    if config is not None:
        app.config.update(**config)

    db.init_app(app)
    api.init_app(app)
    influx_db.init_app(app)
    menu.init_app(app)

    security.init_app(app, users)

    principal = Principal()
    principal.init_app(app)

    init_signals(app)
    configure_uploads(app, logos)
    app.register_blueprint(bp)

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        if not isinstance(identity, AnonymousIdentity):
            identity.provides.add(UserNeed(identity.id))

            for role in current_user.roles:
                identity.provides.add(RoleNeed(role.name))

    @principal.identity_loader
    def read_identity_from_flask_login():
        if current_user.is_authenticated:
            return Identity(current_user.id)
        return AnonymousIdentity()

    @app.after_request
    def set_cid_cookie(response):
        if 'cid' not in flask.request.cookies:
            cid = str(uuid.uuid4())
            expires = datetime.datetime.now() + datetime.timedelta(days=365*2)
            response.set_cookie('cid', cid, expires=expires)
        return response

    return app

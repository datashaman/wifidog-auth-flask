# -*- coding: utf-8 -*-
"""
Create app
"""

from __future__ import absolute_import

import datetime
import uuid

import six

from app import constants

from app.models import User, Role, db, users
from app.resources import GatewayResource, \
        NetworkResource, \
        UserResource, \
        VoucherResource, \
        api, \
        logos
from app.services import login_manager, mail, menu, security
from app.views import bp

from flask import Flask, request
from flask_uploads import configure_uploads
from flask_principal import \
        AnonymousIdentity, \
        Identity, \
        Principal, \
        RoleNeed, \
        UserNeed, \
        identity_loaded
from flask_security import AnonymousUser, current_user

def create_app(config=None):
    """ Create app """

    app = Flask(__name__)

    app.config.from_object('config')

    if config is not None:
        app.config.update(**config)

    db.init_app(app)
    api.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    menu.init_app(app)

    security.init_app(app, users)

    principal = Principal()
    principal.init_app(app)

    configure_uploads(app, logos)
    app.register_blueprint(bp)

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        """Load needs onto the identity"""
        if not isinstance(identity, AnonymousIdentity):
            identity.provides.add(UserNeed(identity.id))

            for role in current_user.roles:
                identity.provides.add(RoleNeed(role.name))

    @principal.identity_loader
    def read_identity_from_flask_login():
        """Convert flask login to identity"""
        if hasattr(current_user, 'id'):
            return Identity(current_user.id)
        return AnonymousIdentity()

    @app.after_request
    def set_cid_cookie(response):
        """Set CID cookie to hold session together"""
        if 'cid' not in request.cookies:
            cid = str(uuid.uuid4())
            expires = datetime.datetime.now() + datetime.timedelta(days=365*2)
            response.set_cookie('cid', cid, expires=expires)
        return response

    @app.context_processor
    def context_processor():
        """Context processors for use in templates"""
        return dict(constants=constants, six=six)

    return app

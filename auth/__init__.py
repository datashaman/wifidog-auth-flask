# -*- coding: utf-8 -*-
"""
Create app
"""

from __future__ import absolute_import

import datetime
import os
import pytz
import uuid

import six

from auth import constants

from auth.models import User, Role, db, users
from auth.resources import GatewayResource, \
        NetworkResource, \
        UserResource, \
        VoucherResource, \
        api, \
        logos
from auth.services import login_manager, mail, menu, security
from auth.views import bp

from dateutil.tz import tzlocal

from flask import Flask
from flask_uploads import configure_uploads
from flask_principal import \
        AnonymousIdentity, \
        Identity, \
        Principal, \
        RoleNeed, \
        UserNeed, \
        identity_loaded
from flask_security import current_user


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

    configure_uploads(app, (logos,))
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
    def security_measures(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1"
        if 'Cache-Control' not in response.headers:
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        return response

    @app.template_filter()
    def local_datetime(value, format="%I:%M %p"):
        tz = tzlocal()
        utc = pytz.timezone('UTC')
        value = utc.localize(value, is_dst=None).astimezone(pytz.utc)
        local_dt = value.astimezone(tz)
        return local_dt.strftime(format)

    @app.context_processor
    def context_processor():
        """Context processors for use in templates"""
        return dict(constants=constants, six=six)

    return app

# -*- coding: utf-8 -*-
"""
Create app
"""

from __future__ import absolute_import

import six
import logging

from auth import constants
from auth.models import db, users
from auth.processors import init_processors
from auth.services import login_manager, logos, mail, menu, security
from auth.utils import render_currency_amount
from auth.views import bp
from flask import Flask, render_template, request
from flask_babelex import Babel
from flask_uploads import configure_uploads
from flask_security import current_user
from logging.handlers import SMTPHandler


def create_app(config=None):
    """ Create app """
    app = Flask(__name__)
    app.config.from_object('config')
    if config is not None:
        app.config.update(**config)

    if not app.debug:
        mail_handler = SMTPHandler(app.config['MAIL_SERVER'],
                                   app.config['MAIL_DEFAULT_SENDER'][1],
                                   app.config['ADMINS'],
                                   app.config['MAIL_ERROR_SUBJECT'])
        mail_handler.setFormatter(logging.Formatter('''
    Message type:       %(levelname)s
    Location:           %(pathname)s:%(lineno)d
    Module:             %(module)s
    Function:           %(funcName)s
    Time:               %(asctime)s

    Message:

    %(message)s
'''))

        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    init_processors(app)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    menu.init_app(app)

    security.init_app(app, users)
    configure_uploads(app, (logos,))
    app.register_blueprint(bp)

    babel = Babel(app)

    @babel.localeselector
    def get_locale():
        if not current_user.is_anonymous:
            return current_user.locale

        return request.accept_languages.best_match(app.config['SUPPORTED_LOCALES'])

    @babel.timezoneselector
    def get_timezone():
        if not current_user.is_anonymous:
            return current_user.timezone

    @app.after_request
    def security_measures(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1"
        if 'Cache-Control' not in response.headers:
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        return response

    @app.context_processor
    def context_processor():
        """Context processors for use in templates"""
        return dict(constants=constants,
                    render_currency_amount=render_currency_amount,
                    six=six)

    @app.errorhandler(404)
    def error_handler_404(error):
        return render_template('error.html',
                               error=error,
                               page_title='Not Found',
                               header=404,
                               description="We can't seem to find the page you're looking for."), 404

    @app.errorhandler(500)
    def error_handler_500(error):
        return render_template('error.html',
                               error=error,
                               page_title='Internal Server Error',
                               header=500,
                               description="Oops, looks like something went wrong."), 500

    return app

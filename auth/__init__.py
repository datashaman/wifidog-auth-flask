"""
Create app
"""

from __future__ import absolute_import

import logging
import os

from auth import constants
from auth.blueprints import \
    cashup, \
    category, \
    country, \
    currency, \
    gateway, \
    network, \
    order, \
    product, \
    transaction, \
    user, \
    voucher, \
    wifidog
from auth.models import db, Processor, users
from auth.processors import init_processors
from auth.services import \
    login_manager, \
    logos, \
    mail, \
    menu, \
    security
from auth.views import bp
from flask import Flask, render_template, request
from flask_babelex import Babel
from flask_uploads import configure_uploads
from flask_security import current_user
from logging.handlers import SMTPHandler
from wtforms import fields


def create_app(config=None):
    """ Create app """
    instance_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance')

    app = Flask(__name__, instance_path=instance_path, instance_relative_config=True)
    env = os.environ.get('FLASK_ENV')
    if not env:
        raise Exception('FLASK_ENV is not set')
    app.config.from_object('auth.default_settings')
    app.config.from_object('settings.%s' % env)
    app.config.from_pyfile('%s.cfg' % env, silent=True)

    if config is not None:
        app.config.update(**config)

    if not app.debug:
        mailhost = app.config.get('ERROR_MAIL_SERVER',
                                  app.config.get('MAIL_SERVER',
                                                 'localhost'))
        mail_handler = SMTPHandler(mailhost,
                                   app.config.get('MAIL_DEFAULT_SENDER',
                                                  'no-reply@localhost'),
                                   app.config['ADMINS'],
                                   app.config.get('ERROR_MAIL_SUBJECT',
                                                  'Application Error'))
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
    app.register_blueprint(cashup, url_prefix='/cashups')
    app.register_blueprint(category, url_prefix='/categories')
    app.register_blueprint(country, url_prefix='/countries')
    app.register_blueprint(currency, url_prefix='/currencies')
    app.register_blueprint(gateway, url_prefix='/gateways')
    app.register_blueprint(network, url_prefix='/networks')
    app.register_blueprint(order, url_prefix='/orders')
    app.register_blueprint(product, url_prefix='/products')
    app.register_blueprint(transaction, url_prefix='/transactions')
    app.register_blueprint(user, url_prefix='/users')
    app.register_blueprint(voucher, url_prefix='/vouchers')
    app.register_blueprint(wifidog, url_prefix='/wifidog')

    babel = Babel(app)

    @babel.localeselector
    def get_locale():
        if not current_user.is_anonymous:
            return current_user.locale

        return request.accept_languages \
                      .best_match(app.config['SUPPORTED_LOCALES'])

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
                    f=fields,
                    international_processors=lambda: Processor.query
                                                              .filter_by(international=True, active=True)
                                                              .all())

    @app.errorhandler(403)
    def error_handler_403(error):
        error_description = error.description if app.debug else None
        return render_template('error.html',
                               error_description=error_description,
                               page_title='Forbidden',
                               header=403,
                               description="You've gone the wrong way."), 403

    @app.errorhandler(404)
    def error_handler_404(error):
        error_description = error.description if app.debug else None
        return render_template('error.html',
                               error_description=error_description,
                               page_title='Not Found',
                               header=404,
                               description="We can't find the page you're looking for."), 404

    @app.errorhandler(500)
    def error_handler_500(error):
        error_description = error.description if app.debug else None
        return render_template('error.html',
                               error_description=error_description,
                               page_title='Internal Server Error',
                               header=500,
                               description="Oops, looks like something went wrong."), 500

    return app

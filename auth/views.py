"""
Views for the app
"""

from __future__ import absolute_import
from __future__ import division

import os

from auth.services import \
        environment_dump, \
        healthcheck as healthcheck_service
from auth.utils import has_role
from flask import \
    Blueprint, \
    abort, \
    current_app, \
    redirect, \
    request, \
    send_from_directory, \
    url_for
from flask_security import \
    auth_token_required, \
    current_user, \
    login_required


bp = Blueprint('auth', __name__)


@bp.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('favicon.ico')


@bp.route('/uploads/<path:path>')
def uploads(path):
    directory = os.path.join(current_app.instance_path, 'uploads')
    cache_timeout = current_app.get_send_file_max_age(path)
    return send_from_directory(directory,
                               path,
                               cache_timeout=cache_timeout,
                               conditional=True)


@bp.route('/healthcheck')
@auth_token_required
def healthcheck():
    return healthcheck_service.check()


@bp.route('/environment')
@auth_token_required
def environment():
    return environment_dump.dump_environment()


@bp.route('/raise-exception')
@login_required
def raise_exception():
    abort(int(request.args.get('status', 500)))


@bp.route('/')
def home():
    return redirect(url_for('security.login'))

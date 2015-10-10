import flask

from app.services import db
from app.utils import is_logged_in, has_role
from flask.ext.menu import register_menu
from flask.ext.security import login_required, roles_required

from app.forms import NetworkForm
from app.models import Network

bp = flask.Blueprint('networks', __name__, url_prefix='/networks', template_folder='templates', static_folder='static')

@bp.route('/')
@login_required
@roles_required('super-admin')
@register_menu(bp, '.networks', 'Networks', visible_when=has_role('super-admin'), order=10)
def index():
    return flask.render_template('networks/index.html')

@bp.route('/new', methods=[ 'GET', 'POST' ])
@login_required
@roles_required('super-admin')
def new():
    network = Network()
    form = NetworkForm(flask.request.form, network)

    if form.validate_on_submit():
        form.populate_obj(network)
        db.session.add(network)
        db.session.commit()

        flask.flash('Network created')

        return flask.redirect(flask.url_for('.index'))

    return flask.render_template('networks/edit.html', form=form, network=network)

@bp.route('/<network_id>', methods=[ 'GET', 'POST' ])
@login_required
@roles_required('super-admin')
def edit(network_id):
    network = Network.query.filter_by(id=network_id).first_or_404()
    form = NetworkForm(flask.request.form, network)

    if form.validate_on_submit():
        form.populate_obj(network)
        db.session.add(network)
        db.session.commit()

        flask.flash('Network updated')

        return flask.redirect(flask.url_for('.index'))

    return flask.render_template('networks/edit.html', form=form, network=network)

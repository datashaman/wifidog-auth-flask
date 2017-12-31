from auth import constants
from auth.forms import FilterForm, instances
from auth.models import \
    db, \
    Role, \
    User
from auth.resources import \
    resource_delete, \
    resource_index, \
    resource_instance
from auth.utils import \
    has_admin_role, \
    is_logged_in
from flask import \
    abort, \
    Blueprint, \
    current_app, \
    flash, \
    redirect, \
    render_template, \
    request, \
    url_for
from flask_menu import register_menu
from flask_security import \
    current_user, \
    login_required, \
    roles_accepted
from flask_wtf import FlaskForm
from pytz import common_timezones
from wtforms import fields as f, validators
from wtforms.ext.sqlalchemy.fields import \
    QuerySelectField, \
    QuerySelectMultipleField


user = Blueprint('user', __name__, template_folder='templates')


def roles():
    if current_user.has_role('super-admin'):
        return db.session.query(Role).all()
    if current_user.has_role('network-admin'):
        return db.session \
                 .query(Role) \
                 .filter(Role.name == 'gateway-admin').all()
    return []


class LocaleMixin(object):
    def set_locale_choices(self):
        self.locale.choices = [(id, title)
                               for id, title in constants.LOCALES.items()]
        self.timezone.choices = [(timezone, timezone)
                                 for timezone in common_timezones]


class UserForm(FlaskForm, LocaleMixin):
    network = QuerySelectField('Network',
                               allow_blank=True,
                               default=lambda: current_user.network,
                               query_factory=instances('network'))
    gateway = QuerySelectField('Gateway',
                               allow_blank=True,
                               default=lambda: current_user.gateway,
                               query_factory=instances('gateway'))
    email = f.StringField('Email')
    password = f.PasswordField(
        'Password',
        [
            validators.Optional(),
            validators.Length(min=2),
            validators.EqualTo('confirm', message='Passwords must match'),
        ]
    )
    confirm = f.PasswordField('Repeat Password')
    locale = f.SelectField('Locale',
                           default=lambda: current_app.config['BABEL_DEFAULT_LOCALE'])
    timezone = f.SelectField('Timezone', default=lambda: current_app.config['BABEL_DEFAULT_TIMEZONE'])
    active = f.BooleanField('Active', default=True)
    roles = QuerySelectMultipleField('Roles', query_factory=roles)


class MyUserForm(FlaskForm, LocaleMixin):
    email = f.StringField('Email')
    password = f.PasswordField(
        'Password',
        [
            validators.Optional(),
            validators.Length(min=2),
            validators.EqualTo('confirm', message='Passwords must match'),
        ]
    )
    confirm = f.PasswordField('Repeat Password')
    locale = f.SelectField('Locale', default=lambda: current_app.config['BABEL_DEFAULT_LOCALE'])
    timezone = f.SelectField('Timezone', default=lambda: current_app.config['BABEL_DEFAULT_TIMEZONE'])


class UserFilterForm(FilterForm):
    network = QuerySelectField('Network', allow_blank=True, query_factory=instances('network'), blank_text='Select Network')
    gateway = QuerySelectField('Gateway', allow_blank=True, query_factory=instances('gateway'), blank_text='Select Gateway')
    email = f.StringField('Email')


@user.route('/mine', methods=['GET', 'POST'])
@login_required
@register_menu(
    user,
    '.account',
    'My Account',
    visible_when=is_logged_in,
    order=130
)
def mine():
    form = MyUserForm(obj=current_user)
    form.set_locale_choices()

    if form.validate_on_submit():
        if form.password.data == '':
            del form.password
        form.populate_obj(current_user)
        db.session.commit()
        flash('Update successful')
        return redirect('/')
    return render_template('user/current.html',
                           form=form,
                           instance=current_user)


@user.route('/')
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
@register_menu(
    user,
    'users',
    'Users',
    visible_when=has_admin_role(),
    order=90
)
def index():
    return resource_index('user', UserFilterForm(formdata=request.args))


@user.route('/new', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def new():
    form = UserForm()
    form.set_locale_choices()

    if current_user.has_role('gateway-admin'):
        del form.roles

    if form.validate_on_submit():
        user = User()
        form.populate_obj(user)
        db.session.add(user)
        db.session.commit()
        flash('Create %s successful' % user)
        return redirect(url_for('.index'))

    return render_template('user/new.html', form=form)


@user.route('/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def edit(id):
    instance = resource_instance('user', id=id)

    if (current_user.has_role('network-admin')
            and instance.network != current_user.network):
        abort(403)

    if (current_user.has_role('gateway-admin')
            and (instance.network != current_user.network
                 or instance.gateway != current_user.gateway)):
        abort(403)

    form = UserForm(obj=instance)
    form.set_locale_choices()

    if current_user.has_role('network-admin'):
        del form.gateway

    if current_user == instance:
        del form.active
        del form.roles

    if form.validate_on_submit():
        if form.password.data == '':
            del form.password

        form.populate_obj(instance)
        db.session.commit()

        flash('Update %s successful' % instance)
        return redirect(url_for('.index'))

    return render_template('user/edit.html', form=form, instance=instance)


@user.route('/<int:id>/delete', methods=['GET', 'POST'])
@login_required
@roles_accepted('super-admin', 'network-admin', 'gateway-admin')
def delete(id):
    return resource_delete('user', id=id)

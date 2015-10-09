from app import db, manager
from flask.ext.script import prompt, prompt_pass

from .config import ROLES
from .models import datastore, Role

@manager.command
def create_user(email=None, password=None, role=None, network=None, gateway=None):
    if email is None:
        email = prompt('Email')

    if password is None:
        password = prompt_pass('Password')
        confirmation = prompt_pass('Confirm Password')

        if password != confirmation:
            print "Passwords don't match"
            return

    if role == 'network-admin':
        if network is None:
            print 'Network is required for a network admin'
            return
        if gateway is not None:
            print 'Gateway is not required for a network admin'
            return

    if role == 'gateway-admin':
        if network is None:
            print 'Network is required for a gateway admin'
            return
        if gateway is None:
            print 'Gateway is required for a gateway admin'
            return

    user = datastore.create_user(email=email, password=password)

    user.network_id = network
    user.gateway_id = gateway

    if role is not None:
        role = Role.query.filter_by(name=role).first()
        user.roles.append(role)

    db.session.commit()
    print 'User created'

@manager.command
def seed_roles():
    if Role.query.count() == 0:
        for name, description in ROLES.iteritems():
            role = Role()
            role.name = name
            role.description = description
            db.session.add(role)
        db.session.commit()

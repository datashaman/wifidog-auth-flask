from app.config import ROLES
from app.networks.config import NETWORKS
from app.networks.models import Network
from app.models import datastore, Role
from app.services import db, manager
from flask.ext.script import prompt, prompt_pass

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

@manager.command
def seed_networks():
    from app.gateways import Gateway

    if Network.query.count() == 0:
        for network_id, defn in NETWORKS.iteritems():
            network = Network(id=network_id, title=defn['title'], description=defn['description'])
            db.session.add(network)

            for gateway_id, gateway_defn in defn['gateways'].iteritems():
                gateway_defn['id'] = gateway_id
                gateway_defn['network_id'] = network_id
                gateway = Gateway(**gateway_defn)
                db.session.add(gateway)

        db.session.commit()

@manager.command
def expire_vouchers():
    # Vouchers that are in use and have expired
    sql = "delete from vouchers where datetime(started_at, '+' || minutes || ' minutes') < current_timestamp"
    db.engine.execute(text(sql))
    
    # Old vouchers that have not been used yet
    sql = "delete from vouchers where datetime(created_at, '+' || %d || ' minutes') < current_timestamp and started_at is null" % app.config.get('VOUCHER_MAXAGE', 120)
    db.engine.execute(text(sql))

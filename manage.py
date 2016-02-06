#!/usr/bin/env python
# encoding: utf-8

import hmac
import json

from app import create_app, init_db
from app.admin import VoucherAdmin
from app.models import Role, Network, Gateway, Voucher, Country, Currency, Product, db, users
from flask.ext.script import Manager, prompt, prompt_pass
from flask.ext.security.utils import encrypt_password
from flask.ext.migrate import Migrate, MigrateCommand
from hashlib import md5
from sqlalchemy import text, func


ROLES = {
    u'super-admin': u'Super Admin',
    u'network-admin': u'Network Admin',
    u'gateway-admin': u'Gateway Admin'
}

app = create_app()

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

@manager.command
def bootstrap_tests():
    filename = app.config['BASE_DIR'] + '/data/tests.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + filename

    init_db(app)

    create_roles(quiet=True)

    create_network(u'main-network', u'Network', quiet=True)
    create_network(u'other-network', u'Other Network', quiet=True)

    create_gateway(u'main-network', u'main-gateway1', u'Main Gateway #1', quiet=True)
    create_gateway(u'main-network', u'main-gateway2', u'Main Gateway #2', quiet=True)

    create_gateway(u'other-network', u'other-gateway1', u'Other Gateway #1', quiet=True)
    create_gateway(u'other-network', u'other-gateway2', u'Other Gateway #2', quiet=True)

    create_user(u'super-admin@example.com', u'admin', u'super-admin', quiet=True)

    create_user(u'main-network@example.com', u'admin', u'network-admin', u'main-network', quiet=True)
    create_user(u'other-network@example.com', u'admin', u'network-admin', u'other-network', quiet=True)

    create_user(u'main-gateway1@example.com', u'admin', u'gateway-admin', u'main-network', u'main-gateway1', quiet=True)
    create_user(u'main-gateway2@example.com', u'admin', u'gateway-admin', u'main-network', u'main-gateway2', quiet=True)

    create_user(u'other-gateway1@example.com', u'admin', u'gateway-admin', u'other-network', u'other-gateway1', quiet=True)
    create_user(u'other-gateway2@example.com', u'admin', u'gateway-admin', u'other-network', u'other-gateway2', quiet=True)

    create_voucher(u'main-gateway1', 60, 'main-1-1', quiet=True)
    create_voucher(u'main-gateway1', 60, 'main-1-2', quiet=True)
    create_voucher(u'main-gateway2', 60, 'main-2-1', quiet=True)
    create_voucher(u'main-gateway2', 60, 'main-2-2', quiet=True)
    create_voucher(u'other-gateway1', 60, 'other-1-1', quiet=True)
    create_voucher(u'other-gateway1', 60, 'other-1-2', quiet=True)
    create_voucher(u'other-gateway2', 60, 'other-2-1', quiet=True)
    create_voucher(u'other-gateway2', 60, 'other-2-2', quiet=True)

    create_country('ZA', u'South Africa', quiet=True)
    create_currency('ZA', 'ZAR', u'South African Rand', u'R', quiet=True)

    create_product(u'main-network', None, u'90 Minute Voucher', 'ZAR', 3000, 'available')

@manager.command
def create_product(network_id, gateway_id, title, currency_id, price, status='new', quiet=True):
    product = Product()

    product.network_id = network_id
    product.gateway_id = gateway_id
    product.title = title
    product.currency_id = currency_id
    product.price = price
    product.status = status

    db.session.add(product)
    db.session.commit()

    if not quiet:
        print 'Product created: %s - %s' % (product.id, product.title)

@manager.command
def create_country(id, title, quiet=True):
    country = Country()

    country.id = id
    country.title = title

    db.session.add(country)
    db.session.commit()

    if not quiet:
        print 'Country created: %s' % country.id

@manager.command
def create_currency(country_id, id, title, prefix=None, suffix=None, quiet=True):
    currency = Currency()

    currency.country_id = country_id
    currency.id = id
    currency.title = title
    currency.prefix = prefix
    currency.suffix = suffix

    db.session.add(currency)
    db.session.commit()

    if not quiet:
        print 'Currency created: %s' % currency.id

@manager.command
def create_voucher(gateway, minutes=60, code=None, quiet=True):
    voucher = Voucher()

    # Allow explicit setting of code (for tests)
    if code is not None:
        voucher.code = code

    voucher.gateway_id = gateway
    voucher.minutes = minutes

    db.session.add(voucher)
    db.session.commit()

    if not quiet:
        print 'Voucher created: %s:%s' % (voucher.id, voucher.code)

@manager.command
def create_network(id, title, description=None, quiet=True):
    network = Network()
    network.id = id
    network.title = title
    network.description = description
    db.session.add(network)
    db.session.commit()

    if not quiet:
        print 'Network created'

@manager.command
@manager.option('-e', '--email', help='Contact Email')
@manager.option('-p', '--phone', help='Contact Phone')
@manager.option('-h', '--home', help='Home URL')
@manager.option('-f', '--facebook', help='Facebook URL')
def create_gateway(network, id, title, description=None, email=None, phone=None, home=None, facebook=None, logo=None, quiet=True):
    gateway = Gateway()
    gateway.network_id = network
    gateway.id = id
    gateway.title = title
    gateway.description = description
    gateway.contact_email = email
    gateway.contact_phone = phone
    gateway.url_home = home
    gateway.url_facebook = facebook
    db.session.add(gateway)
    db.session.commit()

    if not quiet:
        print 'Gateway created'

@manager.command
def create_user(email, password, role, network=None, gateway=None, quiet=True):
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

    user = users.create_user(email=email, password=encrypt_password(password))

    user.network_id = network
    user.gateway_id = gateway

    if role is not None:
        role = Role.query.filter_by(name=role).first()
        user.roles.append(role)

    db.session.commit()

    if not quiet:
        print 'User created'

@manager.command
def create_roles(quiet=True):
    if Role.query.count() == 0:
        for name, description in ROLES.iteritems():
            role = Role()
            role.name = name
            role.description = description
            db.session.add(role)
        db.session.commit()

        if not quiet:
            print 'Roles created'

@manager.command
def process_vouchers():
    # Active vouchers that should end
    vouchers = Voucher.query \
                .filter(Voucher.status == 'active') \
                .all()

    for voucher in vouchers:
        if voucher.should_end():
            voucher.end()
    
    # New vouchers that are unused and should expire
    max_age = app.config.get('VOUCHER_MAXAGE', 120)
    vouchers = Voucher.query \
                .filter(Voucher.status == 'new') \
                .all()

    for voucher in vouchers:
        if voucher.should_expire():
            voucher.expire()

    # Blocked, ended and expired vouchers that should be archived
    vouchers = Voucher.query \
                .filter(func.datetime(Voucher.updated_at, str(max_age) + ' minutes') < func.current_timestamp()) \
                .filter(Voucher.status.in_([ 'blocked', 'ended', 'expired' ])) \
                .all()

    for voucher in vouchers:
        voucher.archive()

    db.session.commit()

@manager.command
def generate_key():
    print hmac.new("datashaman:something", "something", md5).hexdigest()


@manager.command
def measurements():
    (incoming, outgoing) = db.session.query(func.sum(Voucher.incoming), func.sum(Voucher.outgoing)).filter(Voucher.status == 'active').first()

    measurements = {
            'vouchers': {
                'active': Voucher.query.filter_by(status='active').count(),
                'blocked': Voucher.query.filter_by(status='blocked').count(),
                'incoming': incoming,
                'outgoing': outgoing,
                'both': incoming + outgoing,
            }
    }

    return json.dumps(measurements)
    
if __name__ == '__main__':
    manager.run()

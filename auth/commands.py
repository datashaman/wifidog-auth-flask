# encoding: utf-8

from __future__ import absolute_import

import csv
import datetime
import simplejson as json

from auth.constants import ROLES
from auth.models import \
    Cashup, \
    Category, \
    Change, \
    Country, \
    Currency, \
    Gateway, \
    GatewayType, \
    Network, \
    Order, \
    OrderItem, \
    Processor, \
    Product, \
    Role, \
    Transaction, \
    User, \
    Voucher, \
    country_currencies, \
    country_processors, \
    db, \
    roles_users, \
    users
from auth.services import manager
from flask import current_app
from flask_script import prompt, prompt_pass
from flask_security.utils import encrypt_password
from sqlalchemy import func, inspect, Table
from sqlalchemy.orm import Session


@manager.command
def bootstrap_instance(country_id, country_title, bind=None, users_csv=None):
    db.create_all(bind=bind)

    create_category(None, None, u'vouchers', u'Vouchers', properties='minutes\nmegabytes', read_only=True)
    create_country(country_id, country_title)
    create_processor('cash', 'Cash', active=True, international=True)
    create_gateway_types()
    create_roles()

    if users_csv:
        with open(users_csv) as f:
            for user in csv.reader(f):
                create_user(*user)


@manager.command
def bootstrap_reference(bind=None, users_csv=None):
    bootstrap_instance('ZA', 'South Africa', bind=bind, users_csv=users_csv)
    create_currency('ZA', 'ZAR', 'South African Rand', 'R')
    create_processor('snapscan', 'SnapScan', 'ZA', active=True)
    create_processor('payu', 'PayU', 'ZA', active=True)


@manager.command
def bootstrap_tests():
    bootstrap_reference()

    create_network(u'main-network', u'Network', u'ZAR')
    create_network(u'other-network', u'Other Network', u'ZAR')

    create_gateway(u'main-network', u'main-gateway1', u'cafe', u'Main Gateway #1')
    create_gateway(u'main-network', u'main-gateway2', u'cafe', u'Main Gateway #2')

    create_gateway(u'other-network', u'other-gateway1', u'cafe', u'Other Gateway #1')
    create_gateway(u'other-network', u'other-gateway2', u'cafe', u'Other Gateway #2')

    create_user(u'super-admin@example.com', 'admin', u'super-admin')

    create_user(u'main-network@example.com', u'admin', u'network-admin', u'main-network')
    create_user(u'other-network@example.com', u'admin', u'network-admin', u'other-network')

    create_user(u'main-gateway1@example.com', u'admin', u'gateway-admin', u'main-network', u'main-gateway1')
    create_user(u'main-gateway2@example.com', u'admin', u'gateway-admin', u'main-network', u'main-gateway2')

    create_user(u'other-gateway1@example.com', u'admin', u'gateway-admin', u'other-network', u'other-gateway1')
    create_user(u'other-gateway2@example.com', u'admin', u'gateway-admin', u'other-network', u'other-gateway2')

    create_voucher(u'main-gateway1', 60, 'main-1-1')
    create_voucher(u'main-gateway1', 60, 'main-1-2')
    create_voucher(u'main-gateway2', 60, 'main-2-1')
    create_voucher(u'main-gateway2', 60, 'main-2-2')
    create_voucher(u'other-gateway1', 60, 'other-1-1')
    create_voucher(u'other-gateway1', 60, 'other-1-2')
    create_voucher(u'other-gateway2', 60, 'other-2-1')
    create_voucher(u'other-gateway2', 60, 'other-2-2')

    create_product(u'main-network', None, u'vouchers', u'90MIN', u'90 Minute Voucher', 30, 'available')


@manager.command
def create_category(network_id, gateway_id, code, title, quiet=True, **kwargs):
    category = Category()
    category.network_id = network_id
    category.gateway_id = gateway_id
    category.code = code
    category.title = title

    for k, v in kwargs.items():
        setattr(category, k, v)

    db.session.add(category)
    db.session.commit()

    if not quiet:
        print('Category created')


@manager.command
def create_product(network_id, gateway_id, category_code, code, title, price, status='new', quiet=True):
    product = Product()
    product.network_id = network_id
    product.gateway_id = gateway_id
    product.category = Category.query.filter_by(code=category_code).first_or_404()
    product.code = code
    product.title = title
    product.price = price
    product.status = status

    db.session.add(product)
    db.session.commit()

    if not quiet:
        print('Product created: %s - %s' % (product.id, product.title))


@manager.command
def create_country(id, title, quiet=True):
    country = Country()

    country.id = id
    country.title = title

    db.session.add(country)
    db.session.commit()

    if not quiet:
        print('Country created: %s' % country.id)


@manager.command
def create_currency(countries, id, title, prefix=None, suffix=None, quiet=True):
    currency = Currency()

    country_ids = countries.split(',')
    currency.countries = [Country.query.get(country_id) for country_id in country_ids]
    currency.id = id
    currency.title = title
    currency.prefix = prefix
    currency.suffix = suffix

    db.session.add(currency)
    db.session.commit()

    if not quiet:
        print('Currency created: %s' % currency.id)


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
        print('Voucher created: %s:%s' % (voucher.id, voucher.code))


@manager.command
def create_network(id, title, currency_id, description=None, quiet=True):
    network = Network()
    network.id = id
    network.currency_id = currency_id
    network.title = title
    network.description = description
    db.session.add(network)
    db.session.commit()

    if not quiet:
        print('Network created')


@manager.command
@manager.option('-e', '--email', help='Contact Email')
@manager.option('-p', '--phone', help='Contact Phone')
@manager.option('-h', '--home', help='Home URL')
@manager.option('-f', '--facebook', help='Facebook URL')
def create_gateway(network, id, type, title, description=None, email=None, phone=None, home=None, facebook=None, logo=None, quiet=True):
    gateway = Gateway()
    gateway.network_id = network
    gateway.id = id
    gateway.title = title
    gateway.gateway_type_id = type
    gateway.description = description
    gateway.contact_email = email
    gateway.contact_phone = phone
    gateway.url_home = home
    gateway.url_facebook = facebook
    db.session.add(gateway)
    db.session.commit()

    if not quiet:
        print('Gateway created')


@manager.command
def create_user(email, password, role, network=None, gateway=None, quiet=True):
    if email is None:
        email = prompt('Email')

    if password is None:
        password = prompt_pass('Password')
        confirmation = prompt_pass('Confirm Password')

        if password != confirmation:
            print("Passwords don't match")
            return

    if role == 'network-admin':
        if network is None:
            print('Network is required for a network admin')
            return
        if gateway is not None:
            print('Gateway is not required for a network admin')
            return

    if role == 'gateway-admin':
        if network is None:
            print('Network is required for a gateway admin')
            return
        if gateway is None:
            print('Gateway is required for a gateway admin')
            return

    user = users.create_user(email=email, password=encrypt_password(password))

    user.network_id = network
    user.gateway_id = gateway
    user.confirmed_at = datetime.datetime.now()

    if role is not None:
        role = Role.query.filter_by(name=role).first()
        user.roles.append(role)

    db.session.commit()

    if not quiet:
        print('User created')


@manager.command
def auth_token(email):
    return users.get_user(email).get_auth_token()


@manager.command
def create_roles(quiet=True):
    if Role.query.count() == 0:
        for name, description in ROLES.items():
            create_role(name, description, quiet)
        if not quiet:
            print('Roles created')


@manager.command
def create_role(name, description, quiet=True):
    role = users.create_role(name=name, description=description)
    db.session.add(role)
    db.session.commit()
    if not quiet:
        print('Role created')


@manager.command
def create_processor(id, title, countries=None, active=False, international=False, quiet=True):
    processor = Processor()
    processor.id = id
    processor.title = title
    processor.active = active
    processor.international = international
    if countries:
        for country_id in countries.split(','):
            country = Country.query.get(country_id)
            processor.countries.append(country)
    db.session.add(processor)
    db.session.commit()

    if not quiet:
        print('Processor created')


@manager.command
def create_gateway_types(quiet=True):
    types = {
        'airline': u'Airline',
        'airport': u'Airport Terminal/Lounge',
        'business-center': u'Business/Conference Center',
        'bus-station': u'Bus Station',
        'cafe': u'Cafe/Coffee Shop',
        'camp-ground': u'Camp Ground',
        'community-network': u'Community Network',
        'convention-center': u'Convention Center',
        'copy-center': u'Copy Center/Business Services',
        'cruise-ship': u'Cruise Ship',
        'entertainment-venue': u'Entertainment Venues',
        'gas-station': u'Gas/Petrol Station',
        'hospital': u'Hospital',
        'hotel': u'Hotel',
        'internet-cafe': u'Internet Cafe',
        'kiosk': u'Kiosk',
        'library': u'Library',
        'marina': u'Marina/Harbour',
        'motorway': u'Motorway Travel Center/TruckStop',
        'office': u'Office Building/Complex',
        'other': u'Other',
        'park': u'Park',
        'pay-phone': u'Pay Phone/Booth',
        'port': u'Port/Ferry Terminal',
        'residence': u'Residential Housing/Apt Bldg',
        'restaurant': u'Restaurant/Bar/Pub',
        'school': u'School/University',
        'shopping-center': u'Shopping Center',
        'sports-arena': u'Sports Arena/Venue',
        'store': u'Store/Retail Shop',
        'train-station': u'Train/Rail Station',
        'train': u'Train',
        'water-travel': u'Water Travel',
        'wifi-zone': u'Wi-Fi Zone',
    }

    for id, title in types.items():
        gateway_type = GatewayType()
        gateway_type.id = id
        gateway_type.title = title
        db.session.add(gateway_type)

    db.session.commit()

    if not quiet:
        print('Gateway types created')


@manager.command
def process_vouchers():
    # Active vouchers that should end
    vouchers = Voucher.query \
                .filter(Voucher.status == 'active') \
                .all()

    for voucher in vouchers:
        if voucher.should_end():
            voucher.end()
            db.session.add(voucher)

    # New vouchers that are unused and should expire
    max_age = current_app.config.get('VOUCHER_MAXAGE', 120)
    vouchers = Voucher.query \
                .filter(Voucher.status == 'new') \
                .all()

    for voucher in vouchers:
        if voucher.should_expire():
            voucher.expire()
            db.session.add(voucher)

    # Blocked, ended and expired vouchers that should be archived
    vouchers = Voucher.query \
        .filter(Voucher.updated_at + datetime.timedelta(minutes=max_age) < func.current_timestamp()) \
        .filter(Voucher.status.in_(['blocked', 'ended', 'expired'])) \
        .all()

    for voucher in vouchers:
        voucher.archive()
        db.session.add(voucher)

    db.session.commit()


@manager.command
def measurements():
    (incoming, outgoing) = db.session.query(func.sum(Voucher.incoming), func.sum(Voucher.outgoing)).filter(Voucher.status == 'active').first()

    measurements = {
        'vouchers': {
            'active': Voucher.query.filter_by(status='active').count(),
            'blocked': Voucher.query.filter_by(status='blocked').count(),
            'incoming': incoming,
            'outgoing': outgoing,
            # 'both': incoming + outgoing,
        }
    }

    print(json.dumps(measurements, indent=4))


def clone_row(row):
    new_row = {}
    for k in row.keys():
        new_row[k] = getattr(row, k)
    return new_row


@manager.command
def migrate():
    entities = [
        Currency,
        GatewayType,
        Processor,
        Role,
        Country,
        country_currencies,
        country_processors,
        Network,
        Gateway,
        Category,
        Product,
        User,
        roles_users,
        Change,
        Order,
        OrderItem,
        Voucher,
        Cashup,
        Transaction,
    ]

    reference_engine = db.get_engine(current_app, 'reference')
    reference_session = Session(reference_engine)

    old_engine = db.get_engine(current_app, 'old')
    old_session = Session(old_engine)

    new_engine = db.get_engine(current_app, 'new')
    new_session = Session(new_engine)

    for entity in entities:
        if type(entity) is Table:
            if entity.exists(bind=old_engine):
                rows = old_engine.execute(entity.select())
            else:
                rows = reference_engine.execute(entity.select())

            entity.create(bind=new_engine)
            for values in rows:
                new_session.execute(entity.insert(values))
        else:
            if entity.__table__.exists(bind=old_engine):
                insp = inspect(old_engine)
                columns = [getattr(entity, c['name']) for c in insp.get_columns(entity.__tablename__) if hasattr(entity, c['name'])]
                rows = [clone_row(r) for r in old_session.query(*columns).all()]
            else:
                rows = reference_session.query(entity).all()

            class NewModel(entity):
                __tablename__ = entity.__tablename__
                __bind_key__ = 'new'

            entity.__table__.create(bind=new_engine)

            for row in rows:
                if hasattr(row, '__dict__'):
                    row = row.__dict__

                if '_sa_instance_state' in row:
                    del row['_sa_instance_state']

                if entity.__tablename__ == 'gateways':
                    row['country_id'] = u'ZA'
                    row['gateway_type_id'] = 'cafe'

                if entity.__tablename__ == 'networks':
                    row['currency_id'] = u'ZAR'

                if entity.__tablename__ == 'orders':
                    row['total_amount'] = row.get('amount', 0)

                if entity.__tablename__ == 'transactions':
                    row['total_amount'] = row.get('amount', 0)

                if entity.__tablename__ == 'products':
                    row['category_id'] = Category.query.filter_by(code='vouchers').first_or_404().id

                new_session.execute(entity.__table__.insert(row))

        new_session.commit()

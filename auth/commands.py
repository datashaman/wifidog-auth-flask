from __future__ import absolute_import

import csv
import datetime
import simplejson as json
import yaml

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
    VatRate, \
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

    create_category(None, None, 'vouchers', 'Vouchers', properties='minutes\nmegabytes', read_only=True)
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
    create_processor('pay', 'Pay', 'ZA', active=True)
    create_vat_rate('standard', 'Standard Rate', 14, 'ZA')
    create_vat_rate('zero', 'Zero Rate', 0, 'ZA')



@manager.command
def bootstrap_test():
    bootstrap_reference()

    create_network('main-network', 'Network', 'ZAR')
    create_network('other-network', 'Other Network', 'ZAR')

    create_gateway('main-network', 'main-gateway1', 'cafe', 'Main Gateway #1', 'ZA')
    create_gateway('main-network', 'main-gateway2', 'cafe', 'Main Gateway #2', 'ZA')

    create_gateway('other-network', 'other-gateway1', 'cafe', 'Other Gateway #1', 'ZA')
    create_gateway('other-network', 'other-gateway2', 'cafe', 'Other Gateway #2', 'ZA')

    create_user('service@example.com', 'admin123', 'service')

    create_user('super-admin@example.com', 'admin123', 'super-admin')

    create_user('main-network@example.com', 'admin123', 'network-admin', 'main-network')
    create_user('other-network@example.com', 'admin123', 'network-admin', 'other-network')

    create_user('main-gateway1@example.com', 'admin123', 'gateway-admin', 'main-network', 'main-gateway1')
    create_user('main-gateway2@example.com', 'admin123', 'gateway-admin', 'main-network', 'main-gateway2')

    create_user('other-gateway1@example.com', 'admin123', 'gateway-admin', 'other-network', 'other-gateway1')
    create_user('other-gateway2@example.com', 'admin123', 'gateway-admin', 'other-network', 'other-gateway2')

    create_voucher('main-gateway1', 60, 'main-1-1')
    create_voucher('main-gateway1', 60, 'main-1-2')
    create_voucher('main-gateway2', 60, 'main-2-1')
    create_voucher('main-gateway2', 60, 'main-2-2')
    create_voucher('other-gateway1', 60, 'other-1-1')
    create_voucher('other-gateway1', 60, 'other-1-2')
    create_voucher('other-gateway2', 60, 'other-2-1')
    create_voucher('other-gateway2', 60, 'other-2-2')

    create_product('main-network', None, 'vouchers', '90MIN', '90 Minute Voucher', 50, minutes=90, megabytes=500, vat_rate_id='standard')


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
def create_product(network_id, gateway_id, category_code, code, title, price, quiet=True, **kwargs):
    product = Product()
    product.network_id = network_id
    product.gateway_id = gateway_id
    product.category = Category.query.filter_by(code=category_code).first_or_404()
    product.code = code
    product.title = title
    product.price = price

    names = product.category.properties
    names = names.split('\n') if names else []

    properties = {}

    for k, v in kwargs.items():
        if k in names:
            properties[k] = v
        else:
            setattr(product, k, v)

    if properties:
        product.properties = '\n'.join('%s=%s' % (k, v) for k, v in properties.items())

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
def create_gateway(network, id, type, title, country_id, quiet=True, **kwargs):
    gateway = Gateway()
    gateway.network_id = network
    gateway.id = id
    gateway.gateway_type_id = type
    gateway.title = title
    gateway.country_id = country_id

    for k, v in kwargs.items():
        setattr(gateway, k, v)

    db.session.add(gateway)
    db.session.commit()

    if not quiet:
        print('Gateway created')


@manager.command
def create_user(email, password, role, network=None, gateway=None, quiet=True):
    if email is None:
        email = prompt('Email')

    if User.query.filter_by(email=email).count() > 0:
        print('User exists')
        return

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
        'airline': 'Airline',
        'airport': 'Airport Terminal/Lounge',
        'business-center': 'Business/Conference Center',
        'bus-station': 'Bus Station',
        'cafe': 'Cafe/Coffee Shop',
        'camp-ground': 'Camp Ground',
        'community-network': 'Community Network',
        'convention-center': 'Convention Center',
        'copy-center': 'Copy Center/Business Services',
        'cruise-ship': 'Cruise Ship',
        'entertainment-venue': 'Entertainment Venues',
        'gas-station': 'Gas/Petrol Station',
        'hospital': 'Hospital',
        'hotel': 'Hotel',
        'internet-cafe': 'Internet Cafe',
        'kiosk': 'Kiosk',
        'library': 'Library',
        'marina': 'Marina/Harbour',
        'motorway': 'Motorway Travel Center/TruckStop',
        'office': 'Office Building/Complex',
        'other': 'Other',
        'park': 'Park',
        'pay-phone': 'Pay Phone/Booth',
        'port': 'Port/Ferry Terminal',
        'residence': 'Residential Housing/Apt Bldg',
        'restaurant': 'Restaurant/Bar/Pub',
        'school': 'School/University',
        'shopping-center': 'Shopping Center',
        'sports-arena': 'Sports Arena/Venue',
        'store': 'Store/Retail Shop',
        'train-station': 'Train/Rail Station',
        'train': 'Train',
        'water-travel': 'Water Travel',
        'wifi-zone': 'Wi-Fi Zone',
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
    # Active vouchers that should end (time or megabytes are finished).
    for voucher in Voucher.query.filter_by(status='active').all():
        if voucher.should_end() or voucher.megabytes_are_finished():
            voucher.end()

    # New vouchers that are unused and should expire.
    for voucher in Voucher.query.filter_by(status='new').all():
        if voucher.should_expire():
            voucher.expire()

    # Blocked, ended and expired vouchers that should be archived.
    # Keep them for a day maximum.
    # TODO Use config
    vouchers = Voucher.query \
        .filter(Voucher.updated_at + datetime.timedelta(minutes=60 * 24) < func.current_timestamp()) \
        .filter(Voucher.status.in_(['blocked', 'ended', 'expired'])) \
        .all()

    for voucher in vouchers:
        voucher.archive()

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
        VatRate,
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
                    row['country_id'] = 'ZA'
                    row['gateway_type_id'] = 'cafe'

                if entity.__tablename__ == 'networks':
                    row['currency_id'] = 'ZAR'

                if entity.__tablename__ == 'orders':
                    row['total_amount'] = row.get('amount', 0)

                if entity.__tablename__ == 'products':
                    row['vat_rate_id'] = 'standard'

                if entity.__tablename__ == 'transactions':
                    row['total_amount'] = row.get('amount', 0)

                if entity.__tablename__ == 'products':
                    row['category_id'] = Category.query.filter_by(code='vouchers').first_or_404().id

                new_session.execute(entity.__table__.insert(row))

        new_session.commit()


@manager.command
def create_vat_rate(id, title, percentage, country_id, quiet=True):
    vat_rate = VatRate()
    vat_rate.id = id
    vat_rate.title = title
    vat_rate.country_id = country_id
    vat_rate.percentage = percentage
    db.session.add(vat_rate)
    db.session.commit()

    if not quiet:
        print('Vat rate created')

@manager.command
def load_gateway_products(gateway_id, products_file):
    gateway = Gateway.query.get_or_404(gateway_id)

    with open(products_file, 'r') as f:
        products = yaml.load(f)

    category_sequence = 0

    for category_code, category_defn in products['categories'].items():
        category_sequence += 10

        category = Category()
        category.code = category_code
        category.description = category_defn.get('description')
        category.sequence = category_sequence
        category.title = category_defn['title']

        product_sequence = 0

        for product_code, product_defn in category_defn['products'].items():
            product_sequence += 10

            product = Product()

            for k, v in products['defaults'].items():
                setattr(product, k, v)

            product.code = product_code
            product.description = product_defn.get('description')
            product.gateway_id = gateway.id
            product.network_id = gateway.network.id
            product.price = product_defn['price']
            product.sequence = product_sequence
            product.title = product_defn['title']
            product.unit = product_defn.get('unit')

            category.products.append(product)

        db.session.add(category)

    db.session.commit()

from app.models import Network, User, Gateway, Voucher
from flask.ext.login import current_user
from flask.ext.potion import fields, signals
from flask.ext.potion.routes import Relation, Route
from flask.ext.potion.contrib.principals import PrincipalResource, PrincipalManager
from flask.ext.security import current_user

super_admin_only = 'super-admin'
network_or_above = ['super-admin', 'network-admin']
gateway_or_above = ['super-admin', 'network-admin', 'gateway-admin']

class Manager(PrincipalManager):
    def instances(self, where=None, sort=None):
        query = PrincipalManager.instances(self, where, sort)

        if current_user.has_role('network-admin'):
            query = query.filter_by(network_id=current_user.network_id)

        if current_user.has_role('gateway-admin'):
            query = query.filter_by(gateway_id=current_user.gateway_id)

        return query

class UserResource(PrincipalResource):
    class Meta:
        manager = Manager

        model = User
        include_id = True
        permissions = {
            'read': gateway_or_above,
            'create': gateway_or_above,
            'update': gateway_or_above,
            'delete': gateway_or_above,
        }
        read_only_fields = ('created_at',)
        write_only_fields = ('password',)

    class Schema:
        network = fields.ToOne('networks')
        gateway = fields.ToOne('gateways')

        email = fields.Email()
        password = fields.String(min_length=6, max_length=20)

    @Route.GET
    def current(self):
        return {
            'id': current_user.id,
            'email': current_user.email,
            'roles': [ r.name for r in current_user.roles ],
            'network': current_user.network_id,
            'gateway': current_user.gateway_id,
        }

class GatewayResource(PrincipalResource):
    users = Relation('users')
    vouchers = Relation('vouchers')

    class Meta:
        manager = Manager

        model = Gateway
        include_id = True
        id_converter = 'string'
        id_field_class = fields.String
        permissions = {
            'read': gateway_or_above,
            'create': network_or_above,
            'update': network_or_above,
            'delete': network_or_above,
        }
        read_only_fields = ('created_at',)

    class Schema:
        id = fields.String(min_length=3, max_length=20)
        network = fields.ToOne('networks')
        title = fields.String(min_length=3)

class NetworkResource(PrincipalResource):
    gateways = Relation('gateways')
    users = Relation('users')

    class Meta:
        manager = Manager

        model = Network
        include_id = True
        id_converter = 'string'
        id_field_class = fields.String
        permissions = {
            'read': gateway_or_above,
            'create': super_admin_only,
            'update': super_admin_only,
            'delete': super_admin_only,
        }
        read_only_fields = ('created_at',)

    class Schema:
        id = fields.String(min_length=3, max_length=20)
        title = fields.String(min_length=3)

class VoucherResource(PrincipalResource):
    class Meta:
        manager = Manager

        model = Voucher
        include_id = True
        id_converter = 'string'
        id_field_class = fields.String
        permissions = {
            'read': gateway_or_above,
            'create': gateway_or_above,
            'update': gateway_or_above,
            'delete': gateway_or_above,
        }
        read_only_fields = ('created_at',)

    class Schema:
        network = fields.ToOne('networks')
        gateway = fields.ToOne('gateways')

@signals.before_create.connect_via(GatewayResource)
@signals.before_create.connect_via(UserResource)
@signals.before_create.connect_via(VoucherResource)
def set_scope(sender, item):
    if current_user.has_role('network-admin') or current_user.has_role('gateway-admin'):
        item.network_id = current_user.network_id

    if current_user.has_role('gateway-admin'):
        item.gateway_id = current_user.gateway_id

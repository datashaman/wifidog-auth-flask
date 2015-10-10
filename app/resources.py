from app.models import Network, User, Gateway, Voucher
from flask.ext.login import current_user
from flask.ext.potion import fields, signals
from flask.ext.potion.routes import Relation, Route
from flask.ext.potion.contrib.principals import PrincipalResource
from flask.ext.security import current_user

super_admin_only = 'super-admin'
network_or_above = ['super-admin', 'network-admin']
gateway_or_above = ['super-admin', 'network-admin', 'gateway-admin']

class UserResource(PrincipalResource):
    class Meta:
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
        model = Gateway
        include_id = True
        id_converter = 'string'
        id_field_class = fields.String
        permissions = {
            'read': network_or_above,
            'create': network_or_above,
            'update': network_or_above,
            'delete': network_or_above,
        }
        read_only_fields = ('created_at',)

    class Schema:
        id = fields.String()
        network = fields.ToOne('networks')

class NetworkResource(PrincipalResource):
    gateways = Relation('gateways')
    users = Relation('users')

    class Meta:
        model = Network
        include_id = True
        id_converter = 'string'
        id_field_class = fields.String
        permissions = {
            'read': super_admin_only,
            'create': super_admin_only,
            'update': super_admin_only,
            'delete': super_admin_only,
        }
        read_only_fields = ('created_at',)

    class Schema:
        id = fields.String()

class VoucherResource(PrincipalResource):
    class Meta:
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

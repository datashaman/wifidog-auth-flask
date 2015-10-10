from app.models import Network, User, Gateway, Voucher
from flask.ext.potion import fields, signals
from flask.ext.potion.routes import Relation
from flask.ext.potion.contrib.principals import PrincipalResource


class UserResource(PrincipalResource):
    class Meta:
        admin_roles = ('super-admin', 'network-admin', 'gateway-admin')

        model = User
        include_id = True
        permissions = {
            'read': admin_roles,
            'create': admin_roles,
            'update': admin_roles,
            'delete': admin_roles,
        }
        read_only_fields = ('created_at',)
        write_only_fields = ('password',)

    class Schema:
        network = fields.ToOne('networks')
        gateway = fields.ToOne('gateways')

class GatewayResource(PrincipalResource):
    users = Relation('users')
    vouchers = Relation('vouchers')

    class Meta:
        admin_roles = ('super-admin', 'network-admin')

        model = Gateway
        include_id = True
        id_converter = 'string'
        id_field_class = fields.String
        permissions = {
            'read': admin_roles,
            'create': admin_roles,
            'update': admin_roles,
            'delete': admin_roles,
        }
        read_only_fields = ('created_at',)

    class Schema:
        id = fields.String()
        network = fields.ToOne('networks')

@signals.before_create.connect_via(GatewayResource)
def on_before_create_gateway(sender, item):
    if current_user.has_role('network-admin'):
        item.network_id = current_user.network_id

class NetworkResource(PrincipalResource):
    gateways = Relation('gateways')
    users = Relation('users')

    class Meta:
        admin_roles = ('super-admin',)

        model = Network
        include_id = True
        id_converter = 'string'
        id_field_class = fields.String
        permissions = {
            'read': admin_roles,
            'create': admin_roles,
            'update': admin_roles,
            'delete': admin_roles,
        }

    class Schema:
        id = fields.String()

class VoucherResource(PrincipalResource):
    class Meta:
        admin_roles = ('super-admin', 'network-admin', 'gateway-admin')

        model = Voucher
        include_id = True
        id_converter = 'string'
        id_field_class = fields.String
        permissions = {
            'read': admin_roles,
            'create': admin_roles,
            'update': admin_roles,
            'delete': admin_roles,
        }
        read_only_fields = ('created_at',)

    class Schema:
        gateway = fields.ToOne('gateways')

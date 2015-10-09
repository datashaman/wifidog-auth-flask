import datetime

from app import db, api
from flask.ext.potion import fields
from flask.ext.potion.contrib.principals import PrincipalResource
from flask.ext.security import current_user

class Gateway(db.Model):
    __tablename__ = 'gateways'

    id = db.Column(db.Unicode, primary_key=True)
    network_id = db.Column(db.Unicode, db.ForeignKey('networks.id'))

    title = db.Column(db.Unicode, nullable=False)
    description = db.Column(db.Unicode, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

admin_roles = [ 'super-admin', 'network-admin' ]

class GatewayResource(PrincipalResource):
    class Meta:
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

api.add_resource(GatewayResource)

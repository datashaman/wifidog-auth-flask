import datetime

from app import db, api
from flask.ext.potion import fields
from flask.ext.potion.contrib.principals import PrincipalResource

class Network(db.Model):
    __tablename__ = 'networks'

    id = db.Column(db.Unicode, primary_key=True)
    title = db.Column(db.Unicode, nullable=False)
    description = db.Column(db.Unicode, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

admin_roles = [ 'super-admin' ]

class NetworkResource(PrincipalResource):
    class Meta:
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

api.add_resource(NetworkResource)

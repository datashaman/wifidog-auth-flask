import datetime

from app import db, api_manager
from marshmallow import Schema, fields

class Gateway(db.Model):
    id = db.Column(db.Unicode, primary_key=True)
    title = db.Column(db.Unicode, nullable=False)
    description = db.Column(db.Unicode, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

class GatewaySchema(Schema):
    id = fields.Str()
    title = fields.Str()
    description = fields.Str()
    created_at = fields.DateTime()

    def make_object(self, data):
        return Gateway(**data)

api_manager.create_api(Gateway, collection_name='gateways', methods=[ 'GET', 'POST', 'DELETE' ])

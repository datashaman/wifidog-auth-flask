import datetime

from app import db, api_manager
from flask.ext.restless import ProcessingException
from flask.ext.security import current_user
from marshmallow import Schema, fields

class Network(db.Model):
    __tablename__ = 'networks'

    id = db.Column(db.Unicode, primary_key=True)
    title = db.Column(db.Unicode, nullable=False)
    description = db.Column(db.Unicode, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

class NetworkSchema(Schema):
    id = fields.Str()
    title = fields.Str()
    description = fields.Str()
    created_at = fields.DateTime()

    def make_object(self, data):
        return Network(**data)

def preprocess_many(search_params=None, **kwargs):
    if search_params is None:
        search_params = {}

    if 'filters' not in search_params:
        search_params['filters'] = []

    if not current_user.has_role('super-admin'):
        raise ProcessingException(description='Not Authorized', code=401)

def preprocess_single(instance_id=None, **kwargs):
    if instance_id is None:
        return

    if current_user.has_role('super-admin'):
        return

    raise ProcessingException(description='Not Authorized', code=401)

api_manager.create_api(Network,
        collection_name='networks',
        methods=[ 'GET', 'POST', 'DELETE', 'PATCH' ],
        preprocessors=dict(
            GET_SINGLE=[preprocess_single],
            GET_MANY=[preprocess_many],
            POST=[preprocess_single],
            PATCH=[preprocess_single],
            DELETE_SINGLE=[preprocess_single],
        ))

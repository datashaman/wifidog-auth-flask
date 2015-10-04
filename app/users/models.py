import datetime

from app import app, db, login_manager, api_manager
from flask.ext.security import UserMixin, RoleMixin, SQLAlchemyUserDatastore, Security
from marshmallow import Schema, fields

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True)
    confirmed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return '<User %r>' % self.email

    def to_dict(self):
        return { c.name: getattr(self, c.name) for c in self.__table__.columns }


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)

datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, datastore)

class UserSchema(Schema):
    id = fields.Int()
    email = fields.Str()
    password = fields.Str()
    created_at = fields.DateTime()

api_manager.create_api(User, collection_name='users', methods=[ 'GET', 'POST', 'DELETE' ], allow_delete_many=True)

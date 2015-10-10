from flask.ext.login import LoginManager, login_required
from flask.ext.menu import Menu
from flask.ext.potion import Api
from flask.ext.principal import Principal
from flask.ext.script import Manager
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security

menu = Menu()
db = SQLAlchemy()
manager = Manager()
login_manager = LoginManager()
api = Api(prefix='/api', decorators=[login_required])
security = Security()
principals = Principal()

import flask

from flask.ext.menu import Menu
from flask.ext.restless import APIManager
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.login import LoginManager

app = flask.Flask(__name__)
app.config.from_object('config')

menu = Menu(app)
db = SQLAlchemy(app)
manager = Manager(app)
api_manager = APIManager(app, flask_sqlalchemy_db=db)
login_manager = LoginManager(app)

import users
import vouchers
import wifidog

app.register_blueprint(users.bp)
app.register_blueprint(vouchers.bp)
app.register_blueprint(wifidog.bp)

db.create_all()

@app.route('/')
def home():
    return flask.render_template('home.html')

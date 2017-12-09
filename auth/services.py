from __future__ import absolute_import

from flask_login import LoginManager
from flask_mail import Mail
from flask_menu import Menu
from flask_script import Manager
from flask_security import Security
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, IMAGES
from healthcheck import HealthCheck, EnvironmentDump

db = SQLAlchemy()
healthcheck = HealthCheck()
environment_dump = EnvironmentDump()
login_manager = LoginManager()
logos = UploadSet('logos', IMAGES)
mail = Mail()
manager = Manager()
menu = Menu()
security = Security()

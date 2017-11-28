from __future__ import absolute_import

from flask_login import LoginManager
from flask_mail import Mail
from flask_menu import Menu
from flask_script import Manager
from flask_security import Security

login_manager = LoginManager()
mail = Mail()
manager = Manager()
menu = Menu()
security = Security()

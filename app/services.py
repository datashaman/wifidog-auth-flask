from flask_login import current_user
from flask_menu import Menu
from flask_principal import Identity, AnonymousIdentity, Principal
from flask_script import Manager
from flask_security import Security

manager = Manager()
menu = Menu()
security = Security()

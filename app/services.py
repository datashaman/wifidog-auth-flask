from flask.ext.influxdb import InfluxDB
from flask.ext.login import current_user
from flask.ext.menu import Menu
from flask.ext.principal import Identity, AnonymousIdentity, Principal
from flask.ext.script import Manager
from flask.ext.security import Security

influx_db = InfluxDB()
manager = Manager()
menu = Menu()
security = Security()

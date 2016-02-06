import os

from asbool import asbool
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

dotenv_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path)

APP_VERSION = '0.6.0'
CSRF_SESSION_KEY = os.environ.get('CSRF_SESSION_KEY')
DATABASE_CONNECTION_OPTIONS = {}
DEBUG = True
GOOGLE_ANALYTICS_TRACKING_ID = os.environ.get('GOOGLE_ANALYTICS_TRACKING_ID')
GTM_CONTAINER_ID = os.environ.get('GTM_CONTAINER_ID')
HOST = '0.0.0.0'
INFLUXDB_DATABASE = 'auth'
INFLUXDB_USER = os.environ.get('INFLUXDB_USER')
INFLUXDB_PASSWORD = os.environ.get('INFLUXDB_PASSWORD')
PORT = 8080
PUSH_ENABLED = False
SECRET_KEY = os.environ.get('SECRET_KEY')
SECURITY_PASSWORD_HASH = 'sha512_crypt'
SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT')
SECURITY_POST_LOGIN_VIEW = 'app.vouchers_index'
SECURITY_POST_LOGOUT_VIEW = 'login'
SECURITY_REGISTERABLE=False
SECURITY_REGISTER_EMAIL=False
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
SQLALCHEMY_TRACK_MODIFICATIONS = False
TESTING = asbool(os.environ.get('TESTING', False))
THREADS_PER_PAGE = 8
UPLOADS_DEFAULT_DEST = os.path.join(BASE_DIR, 'uploads')
UPLOADS_DEFAULT_URL = '/static'
VOUCHER_DEFAULT_MINUTES = 90
VOUCHER_MAXAGE = 60 * 24
WTF_CSRF_ENABLED = asbool(os.environ.get('WTF_CSRF_ENABLED', True))

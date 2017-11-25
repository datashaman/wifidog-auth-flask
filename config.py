import os

from asbool import asbool
from dotenvy import load_env, read

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

TESTING = asbool(os.environ.get('TESTING', False))

if TESTING:
    env_file = '.env.tests'
else:
    env_file = '.env'

dotenv_path = os.path.join(BASE_DIR, env_file)

if os.path.isfile(dotenv_path):
    with open(dotenv_path) as dotenv_file:
        load_env(read(dotenv_file))

APP_VERSION = '0.8.0'
DATABASE_CONNECTION_OPTIONS = {}
DEBUG = asbool(os.environ.get('DEBUG', True))
GOOGLE_ANALYTICS_TRACKING_ID = os.environ.get('GOOGLE_ANALYTICS_TRACKING_ID')
GTM_CONTAINER_ID = os.environ.get('GTM_CONTAINER_ID')
HOST = os.environ.get('HOST', '127.0.0.1')
PORT = os.environ.get('PORT', 8080)
PUSH_ENABLED = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'secret')
SECURITY_CONFIRMABLE = True
SECURITY_PASSWORD_HASH = 'sha512_crypt'
SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', 'secret')
SECURITY_POST_LOGIN_VIEW = 'app.vouchers_index'
SECURITY_POST_LOGOUT_VIEW = 'login'
SECURITY_RECOVERABLE = True
SECURITY_REGISTERABLE = False
SECURITY_REGISTER_EMAIL = False
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
SQLALCHEMY_TRACK_MODIFICATIONS = False
THREADS_PER_PAGE = 8
UPLOADS_DEFAULT_DEST = os.path.join(BASE_DIR, 'uploads')
UPLOADS_DEFAULT_URL = '/static'
VOUCHER_MAXAGE = 60 * 24
WTF_CSRF_ENABLED = asbool(os.environ.get('WTF_CSRF_ENABLED', True))
WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY', 'secret')

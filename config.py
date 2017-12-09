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

ADMINS = os.environ.get('ADMINS', '').split(',')
DATABASE_CONNECTION_OPTIONS = {}
DEFAULT_COUNTRY = os.environ.get('DEFAULT_COUNTRY')
GOOGLE_ANALYTICS_TRACKING_ID = os.environ.get('GOOGLE_ANALYTICS_TRACKING_ID')
GTM_CONTAINER_ID = os.environ.get('GTM_CONTAINER_ID')
HOST = os.environ.get('HOST', '127.0.0.1')
MAIL_DEFAULT_SENDER = [os.environ.get('MAIL_DEFAULT_SENDER_NAME'),
                       os.environ.get('MAIL_DEFAULT_SENDER_EMAIL')]
MAIL_ERROR_SUBJECT = os.environ.get('MAIL_ERROR_SUBJECT')
MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
MAIL_PORT = os.environ.get('MAIL_PORT', 25)
PAYU_PASSWORD = os.environ.get('PAYU_PASSWORD')
PAYU_SAFEKEY = os.environ.get('PAYU_SAFEKEY')
PAYU_URL = os.environ.get('PAYU_URL', 'https://staging.payu.co.za/rpp.do')
PAYU_USERNAME = os.environ.get('PAYU_USERNAME')
PAYU_WSDL = os.environ.get('PAYU_WSDL', 'https://staging.payu.co.za/service/PayUAPI?wsdl')
PORT = os.environ.get('PORT', 8080)
PUSH_ENABLED = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'secret')
SECURITY_CONFIRMABLE = True
SECURITY_PASSWORD_HASH = 'sha512_crypt'
SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', 'secret')
SECURITY_POST_LOGIN_VIEW = 'auth.voucher_index'
SECURITY_POST_LOGOUT_VIEW = 'login'
SECURITY_RECOVERABLE = True
SECURITY_REGISTERABLE = False
SECURITY_REGISTER_EMAIL = False
SNAPSCAN_ENDPOINT = os.environ.get('SNAPSCAN_ENDPOINT', 'https://pos.snapscan.io/merchant/api/v1')
SNAPSCAN_API_KEY = os.environ.get('SNAPSCAN_API_KEY')
SNAPSCAN_SNAP_CODE = os.environ.get('SNAPSCAN_SNAP_CODE')
SUPPORTED_LOCALES = ['en']
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
SQLALCHEMY_BINDS = {
    'reference': 'sqlite:///../data/reference.db',
    'old': 'sqlite:///../data/old.db',
    'new': 'sqlite:///../data/new.db',
}
SQLALCHEMY_TRACK_MODIFICATIONS = False
THREADS_PER_PAGE = 8
UPLOADS_DEFAULT_DEST = os.path.join(BASE_DIR, 'auth/static/uploads')
UPLOADS_DEFAULT_URL = '/static/uploads'
VOUCHER_MAXAGE = 60 * 24
WTF_CSRF_ENABLED = asbool(os.environ.get('WTF_CSRF_ENABLED', True))
WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY', 'secret')

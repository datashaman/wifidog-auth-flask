import os

from asbool import asbool

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

ADMINS = os.environ.get('ADMINS', '').split(',')
DATABASE_CONNECTION_OPTIONS = {}
DEFAULT_COUNTRY = os.environ.get('DEFAULT_COUNTRY')
GOOGLE_ANALYTICS_TRACKING_ID = os.environ.get('GOOGLE_ANALYTICS_TRACKING_ID')
GTM_CONTAINER_ID = os.environ.get('GTM_CONTAINER_ID')
HOST = os.environ.get('HOST', '127.0.0.1')
PAYU_PASSWORD = os.environ.get('PAYU_PASSWORD')
PAYU_SAFEKEY = os.environ.get('PAYU_SAFEKEY')
PAYU_URL = os.environ.get('PAYU_URL', 'https://staging.payu.co.za/rpp.do')
PAYU_USERNAME = os.environ.get('PAYU_USERNAME')
PAYU_WSDL = os.environ.get('PAYU_WSDL', 'https://staging.payu.co.za/service/PayUAPI?wsdl')
PORT = os.environ.get('PORT', 8080)
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
    'old': 'sqlite:///../instance/data/old.db',
    'new': 'sqlite:///../instance/data/new.db',
}
SQLALCHEMY_TRACK_MODIFICATIONS = False
THREADS_PER_PAGE = 8
UPLOADS_DEFAULT_DEST = os.path.join(BASE_DIR, 'instance/uploads')
UPLOADS_DEFAULT_URL = '/uploads'
VOUCHER_MAXAGE = 60 * 24
WTF_CSRF_ENABLED = asbool(os.environ.get('WTF_CSRF_ENABLED', True))
WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY', 'secret')

import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

ADMINS = ['admin@example.com']
DATABASE_CONNECTION_OPTIONS = {}
SECURITY_CONFIRMABLE = True
SECURITY_PASSWORD_HASH = 'sha512_crypt'
SECURITY_POST_LOGIN_VIEW = 'auth.voucher_index'
SECURITY_POST_LOGOUT_VIEW = 'login'
SECURITY_RECOVERABLE = True
SECURITY_REGISTERABLE = False
SECURITY_REGISTER_EMAIL = False
SNAPSCAN_ENDPOINT = 'https://pos.snapscan.io/merchant/api/v1'
SUPPORTED_LOCALES = ['en']
SQLALCHEMY_BINDS = {
    'reference': 'sqlite:///../data/reference.db',
    'old': 'sqlite:///../instance/data/old.db',
    'new': 'sqlite:///../instance/data/new.db',
}
SQLALCHEMY_TRACK_MODIFICATIONS = False
THREADS_PER_PAGE = 8
UPLOADS_DEFAULT_DEST = os.path.join(BASE_DIR, 'instance/uploads')
UPLOADS_DEFAULT_URL = '/uploads'
VOUCHER_MAXAGE = 60 * 24 * 30  # 30 Days

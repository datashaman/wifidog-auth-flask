import os

HOST = '0.0.0.0'
PORT = 8080
DEBUG = True
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'data/local.db')
DATABASE_CONNECTION_OPTIONS = {}
THREADS_PER_PAGE = 8
CSRF_ENABLED = True
CSRF_SESSION_KEY = 'ABigSecretIsHardToFind'
SECRET_KEY = 'AnotherBigSecretIsAlsoHardToFind'
VOUCHER_MAXAGE = 120

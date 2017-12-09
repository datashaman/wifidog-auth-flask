AUTH_ALLOWED = 1
AUTH_DENIED = 0
AUTH_ERROR = -1
AUTH_VALIDATION = 5
AUTH_VALIDATION_FAILED = 6

STAGE_COUNTERS = 'counters'
STAGE_LOGIN = 'login'
STAGE_LOGOUT = 'logout'

LOCALES = {
    'en': 'English'
}

ROLES = {
    u'super-admin': u'Super Admin',
    u'network-admin': u'Network Admin',
    u'gateway-admin': u'Gateway Admin',
    u'service': u'Service',
}

STATUS_ICONS = {
    'active': 'bolt',
    'archived': 'trash',
    'blocked': 'thumb-down',
    'ended': 'flag',
    'expired': 'circle-x',
    'new': 'file',
}

ACTIONS = {
    'order': [
        'cancel',
        'uncancel',
        'archive',
    ],
    'transaction': [
        'archive',
    ],
    'voucher': [
        'extend',
        'block',
        'unblock',
        'archive',
    ],
}

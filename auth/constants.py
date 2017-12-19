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
    'super-admin': 'Super Admin',
    'network-admin': 'Network Admin',
    'gateway-admin': 'Gateway Admin',
    'service': 'Service',
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
    'order_item': [
        'delete',
    ],
    'voucher': [
        'extend',
        'block',
        'unblock',
        'archive',
    ],
}

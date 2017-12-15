from __future__ import absolute_import

import simplejson as json

order_actions = {
    'cancel': {
        'interface': 'admin',
        'icon': 'x'
    },
    'pay': {
        'interface': 'admin',
        'icon': 'check'
    },
    'uncancel': {
        'interface': 'admin',
    },
}

order_states = {
    'cancelled': {
        'uncancel': 'new',
    },
    'new': {
        'pay': 'paid',
        'cancel': 'cancelled',
    },
    'paid': {
    },
}

transaction_actions = {}
transaction_states = {}

voucher_actions = {
    'archive': {
        'interface': 'admin',
        'icon': 'x',
    },
    'expire': {
        'interface': 'system',
        'icon': 'clock',
    },
    'end': {
        'interface': 'system',
    },
    'extend': {
        'interface': 'admin',
        'icon': 'timer'
    },
    'login': {
        'interface': 'user',
        'icon': 'enter',
    },
    'block': {
        'interface': 'admin',
        'icon': 'thumb-down',
    },
    'unblock': {
        'interface': 'admin',
        'icon': 'thumb-up',
    },
}

voucher_states = {}

for state in ('new', 'active', 'expired', 'ended', 'blocked'):
    voucher_states[state] = { 'archive': 'archived' }

for ( source, method, destination) in (
    ( 'new', 'expire', 'expired' ),
    ( 'new', 'extend', 'new' ),
    ( 'active', 'extend', 'active' ),
    ( 'active', 'end', 'ended' ),
    ( 'active', 'block', 'blocked' ),
    ( 'blocked', 'unblock', 'active' ),
    ( 'new', 'login', 'active' ),
):
    if source not in voucher_states:
        voucher_states[source] = { 'archive': 'archived' }

    voucher_states[source][method] = destination

if __name__ == '__main__':
    import json
    print('Orders')
    print(json.dumps(order_states, indent=4))

    print('Vouchers')
    print(json.dumps(voucher_states, indent=4))

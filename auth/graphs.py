from __future__ import absolute_import

import simplejson as json

graphs = {
    'adjustment': {
        'actions': {},
        'states': {}
    },

    'order': {
        'actions': {
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
        },
        'states': {
            'cancelled': {
                'uncancel': 'new',
            },
            'new': {
                'pay': 'paid',
                'cancel': 'cancelled',
            },
            'paid': {
            },
        },
    },

    'order_item': {
        'actions': {
            'delete': {
                'interface': 'admin',
                'icon': 'x',
            },
        },
        'states': {},
    },

    'transaction': {
        'actions': {},
        'states': {}
    },

    'voucher': {
        'actions': {
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
        },
        'states': {
            'new': {
                'archive': 'archived',
                'expire': 'expired',
                'extend': 'new',
                'login': 'active',
            },
            'active': {
                'archive': 'archived',
                'extend': 'active',
                'end': 'ended',
                'block': 'blocked',
            },
            'expired': {
                'archive': 'archived',
            },
            'ended': {
                'archive': 'archived',
            },
            'blocked': {
                'archive': 'archived',
                'unblock': 'active',
            }
        },
    },
}

if __name__ == '__main__':
    import simplejson as json
    print(json.dumps(graphs, indent=2))

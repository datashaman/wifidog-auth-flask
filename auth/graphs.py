from __future__ import absolute_import

import six

actions = {
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

def available_actions(status, interface):
    if status in states:
        result = {}
        for action, defn in six.iteritems(actions):
            if action in states[status] and defn['interface'] == interface:
                result[action] = defn
        return result

    return {}

states = {}

for state in ('new', 'active', 'expired', 'ended', 'blocked'):
    states[state] = { 'archive': 'archived' }

for ( source, method, destination) in (
    ( 'new', 'expire', 'expired' ),
    ( 'new', 'extend', 'new' ),
    ( 'active', 'extend', 'active' ),
    ( 'active', 'end', 'ended' ),
    ( 'active', 'block', 'blocked' ),
    ( 'blocked', 'unblock', 'active' ),
    ( 'new', 'login', 'active' ),
):
    if source not in states:
        states[source] = { 'archive': 'archived' }

    states[source][method] = destination

if __name__ == '__main__':
    import json
    print(json.dumps(states, indent=4))

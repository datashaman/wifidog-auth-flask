import json
import pydot

actions = {
    'delete': {
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
    },
    'login': {
        'interface': 'user',
        'icon': 'enter',
    },
    'block': {
        'interface': 'admin',
    },
    'unblock': {
        'interface': 'admin',
    },
}

def available_actions(status, interface):
    if status in states:
        result = {}
        for action, defn in actions.iteritems():
            if action in states[status] and defn['interface'] == interface:
                result[action] = defn
        return result

    return []

states = {}

with file('app/graphs.dot') as f:
    dot = f.read()
    graph = pydot.graph_from_dot_data(dot)

    for node in graph.get_nodes():
        status = node.get_name()
        states[status] = { 'delete': 'deleted' }

    for edge in graph.get_edges():
        source = edge.get_source()

        if source not in states:
            states[source] = { 'delete': 'deleted' }

        method = edge.get_label()
        destination = edge.get_destination()

        states[source][method] = destination

if __name__ == '__main__':
    print json.dumps(states, indent=4)

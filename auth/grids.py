from babel.dates import format_datetime
from flask import render_template
from flask_security import current_user


class Grid(object):
    def __init__(self, args):
        self.args = args

    @property
    def current_sort(self):
        if self.args.get('sort'):
            sort = (
                (self.args.get('sort'), self.args.get('dir')),
            )
            if sort[0][0] not in self.columns.keys():
                raise Exception('Invalid sort value')
            if sort[0][1] not in ['asc', 'desc']:
                raise Exception('Invalid dir value')
        else:
            sort = getattr(self, 'default_sort', ())
        return sort

    def render_actions(self, instance):
        return render_template('shared/actions.html', instance=instance, action_key=getattr(self, 'action_key', 'id'))

    def render_created_at(self, instance):
        return format_datetime(instance.created_at)

    def render_network_gateway(self, instance):
        lines = []
        if self.show_network(instance):
            network = instance.network if hasattr(instance, 'network') else instance.gateway.network
            lines.append(str(network))
        if self.show_gateway(instance):
            if self.show_network(instance):
                lines.append('<br />')
            lines.append(str(instance.gateway))
        return '\n'.join(lines)

    def show_gateway(self, instance):
        return current_user.has_role('super-admin') or \
                current_user.has_role('network-admin')

    def show_network(self, instance):
        return current_user.has_role('super-admin')

    def show_network_gateway(self, instance):
        return current_user.has_role('super-admin') or \
                current_user.has_role('network-admin')

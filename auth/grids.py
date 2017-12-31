from babel.dates import format_datetime
from flask import render_template
from flask_security import current_user


class Grid(object):
    @property
    def show_network(self):
        return current_user.has_role('super-admin')

    @property
    def show_gateway(self):
        return current_user.has_role('super-admin') or \
                current_user.has_role('network-admin')

    def render_network_gateway(self, instance):
        lines = []
        if self.show_network:
            lines.append(str(instance.network))
        if self.show_gateway:
            if self.show_network:
                lines.append('<br />')
            lines.append(str(instance.gateway))
        return '\n'.join(lines)

    def render_created_at(self, order):
        return format_datetime(order.created_at)

    def render_actions(self, instance):
        return render_template('shared/actions.html', instance=instance)

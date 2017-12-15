from flask import request

from auth import constants
from auth.models import Voucher


def matches_voucher(auth, voucher):
    return auth['gateway_id'] == voucher.gateway_id and auth['mac'] == voucher.mac and auth['ip'] == voucher.ip


def process_auth(auth):
    if auth['token'] is None:
        return (constants.AUTH_DENIED, 'No connection token provided')

    voucher = Voucher.query.filter_by(token=auth['token']).first()

    if voucher is None:
        return (constants.AUTH_DENIED, 'Requested token not found: %s' % auth['token'])

    if voucher.ip is None:
        voucher.ip = request.args.get('ip')

    if voucher.status in ['archived', 'blocked', 'ended', 'expired']:
        return (constants.AUTH_DENIED, 'Requested token is the wrong status: %s' % auth['token'])

    if auth['stage'] == constants.STAGE_LOGIN:
        if voucher.started_at is None:
            if voucher.should_expire():
                voucher.expire()
                return (constants.AUTH_DENIED, 'Token has expired: %s' % auth['token'])

            voucher.login()
            return (constants.AUTH_ALLOWED, None)
        else:
            if matches_voucher(auth, voucher):
                if voucher.should_end():
                    voucher.end()
                    return (constants.AUTH_DENIED, 'Token is in use but has ended: %s' % auth['token'])
                if voucher.megabytes_are_finished():
                    voucher.end()
                    return (constants.AUTH_DENIED, 'Token is in use but megabytes are finished: %s' % auth['token'])
                return (constants.AUTH_ALLOWED, 'Token is already in use but details match: %s' % auth['token'])
            return (constants.AUTH_DENIED, 'Token is already in use: %s' % auth['token'])
    elif auth['stage'] in [ constants.STAGE_LOGOUT, constants.STAGE_COUNTERS ]:
        messages = []

        if auth['incoming'] is not None or auth['outgoing'] is not None:
            if auth['incoming'] > voucher.incoming:
                voucher.incoming = auth['incoming']
            else:
                messages.append('Warning: Incoming counter is smaller than stored value; counter not updated')

            if auth['outgoing'] > voucher.outgoing:
                voucher.outgoing = auth['outgoing']
            else:
                messages.append('Warning: Outgoing counter is smaller than stored value; counter not updated')
        else:
            messages.append('Incoming or outgoing counter is missing; counters not updated')

        if auth['stage'] == constants.STAGE_LOGOUT:
            # Ignore this, when you login the timer starts, that's it
            # (at least it is for this model)
            messages.append('Logout is not implemented')

        if voucher.should_end():
            voucher.end()
            return (constants.AUTH_DENIED, 'Token has ended: %s' % auth['token'])

        if voucher.megabytes_are_finished():
            voucher.end()
            return (constants.AUTH_DENIED, 'Token megabytes are finished: %s' % auth['token'])

        return (constants.AUTH_ALLOWED, ' | ' .join(messages))
    else:
        return (constants.AUTH_ERROR, 'Unknown stage: %s' % auth['stage'])

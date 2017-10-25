from __future__ import absolute_import

import flask
import requests

from blinker import Namespace
from flask import current_app
from flask_login import current_user, user_logged_in, user_logged_out

signals = Namespace()

voucher_generated = signals.signal('voucher_generated')
voucher_logged_in = signals.signal('voucher_logged_in')

def send_hit(t, data):
    hit = {
        'v': 1,
        'tid': flask.current_app.config['GOOGLE_ANALYTICS_TRACKING_ID'],
        't': 'event',
    }

    cid = flask.request.cookies.get('cid')

    if cid is not None:
        hit['cid'] = cid

    if current_user.is_authenticated:
        hit['uid'] = getattr(current_user, 'id', None)

    data.update(hit)

    requests.post('http://www.google-analytics.com/collect', data=data)

def send_event(category, action, label=None, value=None):
    if not current_app.config['TESTING']:
        send_hit('event', {
            'ec': category,
            'ea': action,
            'el': label,
            'ev': value,
        })

def on_user_logged_in(sender, user):
    flask.flash('You were logged in')
    send_event('auth', 'login')

def on_user_logged_out(sender, user):
    flask.flash('You were logged out')
    send_event('auth', 'logout')

def on_voucher_generated(sender, voucher):
    send_event('voucher', 'generate')

def on_voucher_logged_in(sender, voucher):
    flask.session['voucher_token'] = voucher.token
    send_event('voucher', 'login')

def init_signals(app):
    user_logged_in.connect(on_user_logged_in, app)
    user_logged_out.connect(on_user_logged_out, app)
    voucher_generated.connect(on_voucher_generated, app)
    voucher_logged_in.connect(on_voucher_logged_in, app)

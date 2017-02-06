from app.utils import has_role
from flask import Blueprint
from flask_menu import register_menu
from redis import StrictRedis, ConnectionError

from gevent import monkey
monkey.patch_all()

bp = Blueprint('push', __name__)
redis = StrictRedis(host='127.0.0.1', port=6379, db=13)

def event_stream():
    channels = [ 'notifications' ]

    pubsub = redis.pubsub()
    pubsub.subscribe(channels)

    count = 0
    while True:
        try:
            for message in pubsub.listen():
                if message['type'] == 'message':
                    yield 'data:%s\n\n' % message['data']
        except ConnectionError:
            while True:
                print('lost connection; trying to reconnect...')

                try:
                    redis.ping()
                except ConnectionError:
                    time.sleep(10)
                else:
                    pubsub.subscribe(channels)
                    break

@bp.route('/broadcast', methods=[ 'GET', 'POST' ])
@register_menu(bp, '.broadcast', 'Broadcast', visible_when=has_role('super-admin'), order=5)
def broadcast():
    form = BroadcastForm(flask.request.form)

    if form.validate_on_submit():
        redis.publish('notifications', form.message.data)
        flask.flash('Message published')
        return flask.redirect(flask.url_for('.broadcast'))

    return flask.render_template('broadcast.html', form=form)

@bp.route('/push')
def push():
    return flask.Response(event_stream(), mimetype='text/event-stream')

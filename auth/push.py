from auth.utils import has_role
from datetime import time
from flask import \
    Blueprint, \
    flash, \
    redirect, \
    render_template, \
    request, \
    Response, \
    url_for
from flask_wtf import FlaskForm
from flask_menu import register_menu
from redis import StrictRedis, ConnectionError
from wtforms import fields as f, validators

from gevent import monkey
monkey.patch_all()

bp = Blueprint('push', __name__)
redis = StrictRedis(host='127.0.0.1', port=6379, db=13)


class BroadcastForm(FlaskForm):
    message = f.StringField('Message', [validators.InputRequired()])


def event_stream():
    channels = ['notifications']

    pubsub = redis.pubsub()
    pubsub.subscribe(channels)

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


@bp.route('/broadcast', methods=['GET', 'POST'])
@register_menu(bp, '.broadcast', 'Broadcast', visible_when=has_role('super-admin'), order=5)
def broadcast():
    form = BroadcastForm(request.form)

    if form.validate_on_submit():
        redis.publish('notifications', form.message.data)
        flash('Message published')
        return redirect(url_for('.broadcast'))

    return render_template('broadcast.html', form=form)


@bp.route('/push')
def push():
    return Response(event_stream(), mimetype='text/event-stream')

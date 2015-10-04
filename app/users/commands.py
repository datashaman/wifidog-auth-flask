from app import db, manager
from flask.ext.script import prompt, prompt_pass

from .models import Role, datastore

@manager.command
def create_admin(email=None, password=None):
    if email is None:
        email = prompt('Email')

    if password is None:
        password = prompt_pass('Password')
        confirmation = prompt_pass('Confirm Password')

        if password != confirmation:
            print "Passwords don't match"
            return

    user = datastore.create_user(email=email, password=password)
    admin = Role.query.filter_by(name='admin').first()
    user.roles.append(admin)
    db.session.commit()

    print 'User created'

@manager.command
def seed_roles():
    if Role.query.count() == 0:
        admin = Role()
        admin.name = 'admin'
        admin.description = 'Admin user'
        db.session.add(admin)
        db.session.commit()

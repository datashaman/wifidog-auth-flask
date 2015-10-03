from app import manager

from .models import Role

@manager.command
def create_admin():
    email = prompt('Email')
    password = prompt_pass('Password')
    confirmation = prompt_pass('Confirm Password')

    if password == confirmation:
        user = datastore.create_user(email=email, password=password)
        admin = Role.query.filter_by(name='admin').first()
        user.roles.append(admin)
        db.session.commit()

        print 'User created'
    else:
        print "Passwords don't match"

@manager.command
def seed_roles():
    admin = Role()
    admin.name = 'admin'
    admin.description = 'Admin user'
    db.session.add(admin)
    db.session.commit()

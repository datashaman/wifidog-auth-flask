import flask

from flask.ext.security import current_user

def is_logged_out():
    return not current_user.is_authenticated()

def is_logged_in():
    return current_user.is_authenticated()

def has_role(role):
    def func():
        return current_user.is_authenticated() and current_user.has_role(role)
    return func

def has_all_roles(*roles):
    def func():
        if current_user.is_authenticated():
            for role in roles:
                if not current_user.has_role(role):
                    return False
            return True
        return False
    return func

def has_a_role(*roles):
    def func():
        if current_user.is_authenticated():
            for role in roles:
                if current_user.has_role(role):
                    return True
        return False
    return func

def args_get(which):
    def func():
        return flask.request.args.get(which)
    return func


from flask.ext.login import current_user

def is_logged_out():
    return not current_user.is_authenticated

def is_logged_in():
    return current_user.is_authenticated

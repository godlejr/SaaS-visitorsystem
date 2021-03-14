from functools import wraps

from flask import redirect, current_app, url_for
from flask_login import current_user


def visitor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        authId = current_user.get_auth.code
        auth_list = [current_app.config['AUTH_VISITOR'],current_app.config['AUTH_APPROVAL'],current_app.config['AUTH_VISIT_ADMIN'],current_app.config['AUTH_ADMIN']]

        if authId in auth_list:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('main.index'))
    return decorated_function


def approval_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        authId = current_user.get_auth.code
        auth_list = [current_app.config['AUTH_APPROVAL'],current_app.config['AUTH_VISIT_ADMIN'],current_app.config['AUTH_ADMIN']]

        if authId in auth_list:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('main.index'))
    return decorated_function

def visit_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        authId = current_user.get_auth.code
        auth_list = [current_app.config['AUTH_VISIT_ADMIN'],current_app.config['AUTH_ADMIN']]

        if authId in auth_list:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('main.index'))
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        authId = current_user.get_auth.code
        auth_list = [current_app.config['AUTH_ADMIN']]

        if authId in auth_list:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('main.index'))
    return decorated_function
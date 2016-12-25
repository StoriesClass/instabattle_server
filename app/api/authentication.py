from flask import g
from flask_httpauth import HTTPBasicAuth
from .errors import unauthorized

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email_or_token, password):
    from app.models import User, AnonymousUser
    print(email_or_token)
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    return unauthorized("Invalid credentials")


def not_anonymous_required(func):
    def func_wrapper(*args, **kwargs):
        if not g.current_user.is_anonymous:
            return func(*args, **kwargs)
        else:
            return unauthorized("Login required for this endpoint")
    return func_wrapper

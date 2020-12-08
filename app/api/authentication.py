from flask import abort
from flask import g
from flask_httpauth import HTTPBasicAuth
from app.models import Permission

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username_or_token, password):
    from app.models import User, AnonymousUser
    if username_or_token == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(username_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(username=username_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


def not_anonymous_required(func):
    def func_wrapper(*args, **kwargs):
        if not g.current_user.is_anonymous:
            return func(*args, **kwargs)
        else:
            abort(401, message="Login required for this endpoint")

    return func_wrapper


def id_or_admin_required(func):
    def func_wrapper(*args, **kwargs):
        if g.current_user.id == args[0] or g.current_user.role == Permission.ADMINISTER:
            return func(*args, **kwargs)
        else:
            abort(403, message="Only administrators may carry out this operation on another user")

    return func_wrapper

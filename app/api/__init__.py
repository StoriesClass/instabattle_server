from flask import Blueprint, jsonify
from flask_restful import Api, abort
from webargs.flaskparser import parser

from .resources.Auth import TokenAPI
from .resources.Battles import BattlesListAPI, BattleAPI, BattleEntries, BattleVoting
from .resources.Entries import EntriesListAPI, EntryAPI
from .resources.Users import UsersListAPI, UserAPI, UserResetPassword, UserEntries
from .authentication import auth

api_blueprint = Blueprint('api', __name__)

api = Api(api_blueprint)

api.add_resource(UsersListAPI, '/users/', endpoint='users_list')
api.add_resource(UserAPI, '/users/<user_id>', endpoint='user')
api.add_resource(UserResetPassword, '/users/<user_id>/reset_password', endpoint='user_reset_password')
api.add_resource(UserEntries, '/users/<user_id>/entries', endpoint='user_entries')

api.add_resource(BattlesListAPI, '/battles/', endpoint='battles_list')
api.add_resource(BattleAPI, '/battles/<battle_id>', endpoint='battle')
api.add_resource(BattleEntries, '/battles/<battle_id>/entries', endpoint='battle_entries')
api.add_resource(BattleVoting, '/battles/<battle_id>/voting', endpoint='battle_voting')

api.add_resource(EntriesListAPI, '/entries/', endpoint='entries_list')
api.add_resource(EntryAPI, '/entries/<entry_id>', endpoint='entry')

api.add_resource(TokenAPI, '/token', endpoint='get_token')


@api_blueprint.before_request
@auth.login_required
def before_request():
    pass


@api_blueprint.app_errorhandler(403)
def forbidden(message=None):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


@api_blueprint.app_errorhandler(404)
def page_not_found(e):
    response = jsonify({'error': 'not found'})
    response.status_code = 404
    return response


@api_blueprint.app_errorhandler(500)
def internal_server_error(e):
    response = jsonify({'error': 'internal server error'})
    response.status_code = 500
    return response

# This error handler is necessary for usage with Flask-RESTful
@parser.error_handler
def handle_request_parsing_error(err):
    """webargs error handler that uses Flask-RESTful's abort function to return
    a JSON error response to the client.
    """
    code, msg = getattr(err, 'status_code', 400), getattr(err, 'message', 'Invalid Request')
    abort(code, message=msg)
from flask import Blueprint, jsonify
from flask_restful import Api, abort
from webargs.flaskparser import parser

from .resources.Auth import TokenAPI
from .resources.Battles import BattlesListAPI, BattleAPI, BattleEntries, BattleVoting
from .resources.Entries import EntriesListAPI, EntryAPI
from .resources.Users import UsersListAPI, UserAPI, UserResetPassword, UserEntries, UserVotes
from .authentication import auth

api_blueprint = Blueprint('api', __name__)

api = Api(api_blueprint)

api.add_resource(UsersListAPI, '/users/', endpoint='users_list')
api.add_resource(UserAPI, '/users/<string:username>',
                 '/users/<int:user_id>', endpoint='user')
api.add_resource(UserResetPassword, '/users/<string:username>/reset_password',
                 '/users/<int:user_id>/reset_password', endpoint='user_reset_password')
api.add_resource(UserEntries, '/users/<string:username>/entries',
                 '/users/<int:user_id>/entries', endpoint='user_entries')
api.add_resource(UserVotes, '/users/<int:user_id>/votes',
                 '/users/<string:username>/votes', endpoint='user_votes')

api.add_resource(BattlesListAPI, '/battles/', endpoint='battles_list')
api.add_resource(BattleAPI, '/battles/<int:battle_id>', endpoint='battle')
api.add_resource(BattleEntries, '/battles/<int:battle_id>/entries', endpoint='battle_entries')
api.add_resource(BattleVoting, '/battles/<int:battle_id>/voting', endpoint='battle_voting')

api.add_resource(EntriesListAPI, '/entries/', endpoint='entries_list')
api.add_resource(EntryAPI, '/entries/<int:entry_id>', endpoint='entry')

api.add_resource(TokenAPI, '/token', endpoint='get_token')


@api_blueprint.before_request
@auth.login_required
def before_request():
    pass
    # if not g.current_user.is_anonymous and \
    #        not g.current_user.confirmed:
    #    return forbidden("Unconfirmed account")


@api_blueprint.app_errorhandler(401)
def unauthorized(e):
    response = jsonify({'error': 'unauthorized'})
    response.status_code = 401
    return response


@api_blueprint.app_errorhandler(403)
def forbidden(e):
    response = jsonify({'error': 'forbidden'})
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


@parser.error_handler
def handle_request_parsing_error(err):
    """webargs error handler that uses Flask-RESTful's abort function to return
    a JSON error response to the client.
    """
    abort(422, errors=err.messages)

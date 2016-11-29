from flask import Blueprint
from flask_restful import Api

api_blueprint = Blueprint('api', __name__)
api = Api(api_blueprint)


def create_blueprint():
    from .resources.Users import UsersListAPI, UsersTop, UserAPI, UserResetPassword, UserEntries
    api.add_resource(UsersListAPI, '/users/', endpoint='users_list')
    api.add_resource(UsersTop, '/users/top', endpoint='users_top')
    api.add_resource(UserAPI, '/users/<user_id>', endpoint='user')
    api.add_resource(UserResetPassword, '/users/<user_id>/reset_password', endpoint='user_reset_password')
    api.add_resource(UserEntries, '/users/<user_id>/entries', endpoint='user_entries')

    from .resources.Battles import BattlesListAPI, BattleAPI, BattleEntries, BattleVoting
    api.add_resource(BattlesListAPI, '/battles/', endpoint='battles_list')
    api.add_resource(BattleAPI, '/battles/<battle_id>', endpoint='battle')
    api.add_resource(BattleEntries, '/battles/<battle_id>/entries', endpoint='battle_entries')
    api.add_resource(BattleVoting, '/battles/<battle_id>/voting', endpoint='battle_voting')

    from .resources.Entries import EntriesListAPI, EntryAPI
    api.add_resource(EntriesListAPI, '/entries/', endpoint='entries_list')
    api.add_resource(EntryAPI, '/entries/<entry_id>', endpoint='entry')

    from .resources.Auth import TokenAPI
    api.add_resource(TokenAPI, '/token', endpoint='token')

    return api_blueprint

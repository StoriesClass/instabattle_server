from flask_restful import Resource
from ...models import Battle, User


class BattlesListAPI(Resource):
    def post(self):
        """
        Create new battle
        """
        # FIXME need params
        battle = Battle(name="Battle")


class BattleAPI(Resource):
    def get(self, battle_id):
        """
        Get existing battle
        """
        battle = Battle.get_by_id(battle_id)


    def put(self, battle_id):
        """
        Update battles info
        """
        battle = Battle.get_by_id(battle_id)


class BattleEntries(Resource):
    def get(self, battle_id):
        """
        Get all entries of the battle
        """
        battle = Battle.get_by_id(battle_id)
        entries = battle.get_entries()

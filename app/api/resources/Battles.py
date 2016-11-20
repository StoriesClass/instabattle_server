from flask_restful import Resource


class BattlesListAPI(Resource):
    def post(self):
        """
        Create new battle
        """
        pass


class BattleAPI(Resource):
    def get(self, battle_id):
        """
        Get existing battle
        """
        pass

    def put(self, battle_id):
        """
        Update battles info
        """
        pass


class BattleEntries(Resource):
    def get(self, battle_id):
        """
        Get all entries of the battle
        """
        pass

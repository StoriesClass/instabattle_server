from flask import jsonify, request
from flask_restful import Resource, abort
from ...models import Battle
from ..common import battle_schema, battles_list_schema, entries_list_schema


class BattlesListAPI(Resource):
    def get(self):
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        radius = request.args.get('radius', type=float)
        if latitude and longitude and radius is not None:
            battles = Battle.get_in_radius(latitude, longitude, radius)
        else:
            battles = Battle.get_list()
        return jsonify({"battles": battles_list_schema.dump(battles).data})

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
        if battle is None:
            abort(400, message="Battle could not be found.")
        return jsonify({"battle": battle_schema.dump(battle).data})

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
        if battle is None:
            abort(400, message="Battle could not be found.")
        return jsonify({"entries": entries_list_schema.dump(battle.get_entries()).data})


class BattleVoting(Resource):
    def get(self):
        """
        Get two entries to vote
        """
        pass

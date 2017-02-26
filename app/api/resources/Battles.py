from sqlite3 import IntegrityError

from flask import jsonify
from flask_restful import Resource, abort

from app import db
from app.api.authentication import not_anonymous_required
from app.api.common import BattleSchema, UserSchema
from app.helpers import try_add
from ...models import Battle, User, Vote
from ..common import battle_schema, battles_list_schema, entries_list_schema, vote_schema
from webargs.flaskparser import use_kwargs

class BattlesListAPI(Resource):
    @use_kwargs(UserSchema(only=('latitude', 'longitude', 'radius'), partial=True))
    def get(self, latitude, longitude, radius):
        """
        Get list of battles by latitude, longitude and radius.
        If no arguments is provided returns list of all battles.
        """
        if latitude and longitude and radius:
            battles = Battle.get_in_radius(latitude, longitude, radius)
        elif latitude or longitude or radius:
            abort(400, message="Wrong arguments. Maybe typo?")
        else:
            battles = Battle.get_list()
        return jsonify(battles_list_schema.dump(battles).data)

    # FIXME
    @not_anonymous_required
    @use_kwargs(battle_schema)
    def post(self, latitude, longitude, name, description, radius, user_id=None, username=None):
        """
        Create new battle and return it if it was created.
        """
        creator = User.get_or_404(user_id, username)


        battle = Battle(latitude=latitude,
                        longitude=longitude,
                        name=name,
                        description=description,
                        creator_id=creator.id,
                        radius=radius)

        if try_add(battle):
            response = jsonify(battle_schema.dump(battle).data)
            response.status_code = 201
            return response
        else:
            abort(400, message="Couldn't create new battle")


class BattleAPI(Resource):
    def get(self, battle_id):
        """
        Get existing battle
        """
        battle = Battle.query.get_or_404(battle_id)
        return jsonify(battle_schema.dump(battle).data)

    @use_kwargs(BattleSchema(only=('name', 'description')))
    def put(self, battle_id, name, description):
        """
        Update battle's.
        :return: updated battle
        """
        battle = Battle.query.get_or_404(battle_id)

        if name:
            battle.name = name
        if description:
            battle.description = description

        if try_add(battle):
            return jsonify(battle_schema.dump(battle).data)
        else:
            return abort(400, message="Couldn't update user.")

    def delete(self, battle_id):
        """
        Delete battle.
        :return: deleted battle if delete was successful
        """
        battle = Battle.query.get_or_404(battle_id)
        battle_data = battle_schema.dump(battle).data
        Battle.query.filter_by(id=battle_id).delete()
        try:
            db.session.commit()
            return jsonify(battle_data)
        except IntegrityError as e:
            abort(500, message="Battle exists but we couldn't delete it")


class BattleEntries(Resource):
    def get(self, battle_id, count=None):
        """
        Get all entries of the battle
        """
        battle = Battle.query.get_or_404(battle_id)
        return jsonify(entries_list_schema.dump(battle.get_entries(count)).data)


class BattleVoting(Resource):
    @use_kwargs(BattleSchema(only=("user_id",)))
    def get(self, battle_id, user_id):
        """
        Get two entries to vote
        """
        battle = Battle.query.get_or_404(battle_id)

        try:
            entry1, entry2 = battle.get_voting(user_id)
        except TypeError:
            abort(400, message="Couldn't get voting")

        try:
            return jsonify(entries_list_schema.dump([entry1, entry2]).data)
        except TypeError:
            abort(500, message="Couldn't get dump voting")

    @use_kwargs(vote_schema)
    def post(self, battle_id, voter_id, winner_id, loser_id):
        """
        Create new entry
        """

        vote = Vote(voter_id=voter_id,
                    winner_id=winner_id,
                    loser_id=loser_id,
                    battle_id=battle_id)

        user = User.query.get_or_404(voter_id)
        if user.is_voted(battle_id, loser_id, winner_id):
            abort(400, message="User already voted for this pair")
        else:
            print("User didn't voted so yet")

        if try_add(vote):
            response = jsonify(vote_schema.dump(vote).data)
            response.status_code = 201
            return response
        else:
            abort(400, message="Couldn't create new vote")
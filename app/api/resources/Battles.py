from sqlite3 import IntegrityError
from flask import Response
from flask import g
from flask import jsonify
from flask_restful import Resource, abort
from marshmallow.validate import Range
from webargs import fields

from app import db
from app.api.authentication import not_anonymous_required
from app.api.common import BattleSchema, UserSchema
from app.helpers import try_add
from ...models import Battle, User, Vote, Permission
from ..common import battle_schema, battles_list_schema, entries_list_schema, vote_schema
from webargs.flaskparser import use_kwargs


class BattlesListAPI(Resource):
    @use_kwargs(BattleSchema(only=('latitude', 'longitude', 'radius'), partial=True))
    def get(self, latitude=None, longitude=None, radius=None):
        """
        Get list of battles by latitude, longitude and radius.
        If no arguments is provided returns list of all battles.
        """
        if latitude and longitude and radius:
            battles = Battle.get_in_radius(latitude, longitude, radius)
        elif latitude or longitude or radius:
            abort(400, message="Wrong arguments. Maybe a typo?")
        else:
            battles = Battle.get_list()
        return jsonify(battles_list_schema.dump(battles))

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

        if creator.battle_creation_limit <= 0:
            abort(400, message="You have created too many battles already")

        if try_add(battle):
            response = jsonify(battle_schema.dump(battle))
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
        return jsonify(battle_schema.dump(battle))

    @not_anonymous_required
    @use_kwargs(BattleSchema(only=('name', 'description')))
    def put(self, battle_id, name, description):
        """
        Update battle info
        :return: updated battle
        """
        battle = Battle.query.get_or_404(battle_id)

        if name:
            battle.name = name
        if description:
            battle.description = description

        if try_add(battle):
            return jsonify(battle_schema.dump(battle))
        else:
            return abort(400, message="Couldn't update user.")

    @not_anonymous_required
    def delete(self, battle_id):
        """
        Delete battle
        :return: 204 on success, otherwise 500
        """
        battle = Battle.query.get_or_404(battle_id)

        if battle.creator != g.current_user and g.current_user.role != Permission.ADMINISTER:
            return abort(403, message="Only creator of the battle or administer may delete it")

        Battle.query.filter_by(id=battle_id).delete()
        try:
            db.session.commit()
            return Response(status=204)
        except IntegrityError as e:
            abort(500, message="Battle exists but we couldn't delete it")


class BattleEntries(Resource):
    @use_kwargs({'count': fields.Int(validate=Range(min=1))})
    def get(self, battle_id, count=None):
        """
        Get all entries of the battle
        """
        battle = Battle.query.get_or_404(battle_id)
        return jsonify(entries_list_schema.dump(battle.get_entries(count)))


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
            return jsonify(entries_list_schema.dump([entry1, entry2]))
        except TypeError:
            abort(500, message="Couldn't get dump voting")

    @not_anonymous_required
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
            abort(400, message="User had already voted on this pair")

        if try_add(vote):
            response = jsonify(vote_schema.dump(vote))
            response.status_code = 201
            return response
        else:
            abort(400, message="Couldn't create new vote")

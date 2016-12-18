from sqlite3 import IntegrityError

from flask import jsonify
from flask_restful import Resource, abort

from app import db
from app.helpers import try_add
from ...models import Battle, User, Vote, Entry
from ..common import battle_schema, battles_list_schema, entries_list_schema, vote_schema
from webargs import fields
from webargs.flaskparser import use_args, use_kwargs, parser
from marshmallow import validate


class BattlesListAPI(Resource):

    get_args = {
        'latitude': fields.Float(validate=validate.Range(-90, 90)),
        'longitude': fields.Float(validate=validate.Range(-180, 180)),
        'radius': fields.Float()
    }

    @use_kwargs(get_args)
    def get(self, latitude, longitude, radius):
        """
        Get list of battles by latitude, longitude and radius
        If no arguments is provided returns list of all battles.
        :return: list of battles JSON bump
        """

        if latitude and longitude and radius:
            battles = Battle.get_in_radius(latitude, longitude, radius)
        elif latitude or longitude or radius:
            abort(400, message="Wrong arguments. Maybe typo?")
        else:
            battles = Battle.get_list()
        return jsonify(battles_list_schema.dump(battles).data)

    @use_kwargs(battle_schema)
    def post(self, latitude, longitude, name, description, creator, radius):
        """
        Create new battle
        :return: battle JSON if the battle was created
        """
        print("Creator:", creator)
        creator = User.query.filter_by(username=creator).first_or_404()

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
        :return: battle info in JSON format
        """
        from flask import request
        battle = Battle.get_by_id(battle_id)
        if battle is None:
            abort(404, message="Battle could not be found.")
        return jsonify(battle_schema.dump(battle).data)

    put_args = {
        'name': fields.Str(),
        'description': fields.Str()
    }

    @use_kwargs(put_args)
    def put(self, battle_id, name, description):
        """
        Update battle's info
        :return: updated battle
        """
        battle = Battle.get_by_id(battle_id)
        if not battle:
            return abort(400, message="No such battle.")

        if name:
            battle.name = name
        if description:
            battle.description = description

        db.session.add(battle)
        from sqlalchemy.exc import IntegrityError
        try:
            db.session.commit()
            return jsonify(battle_schema.dump(battle).data)
        except IntegrityError:
            db.session.rollback()
            return abort(400, message="Couldn't update user.")

    def delete(self, battle_id):
        """
        Delete battle.
        :param battle_id:
        :return: deleted battle if delete was successful
        """
        battle = Battle.query.get_or_404(battle_id)
        battle_data = battle_schema.dump(battle).data
        Battle.query.filter_by(id=battle_id).delete()
        try:
            db.session.commit()
            return jsonify(battle_data)
        except IntegrityError as e:
            print(e)
            abort(500, message="Battle exists but we couldn't delete it")


class BattleEntries(Resource):
    def get(self, battle_id, count=None):
        """
        Get all entries of the battle
        """
        battle = Battle.query.get_or_404(battle_id)
        if battle is None:
            abort(404, message="Battle could not be found.")
        return jsonify(entries_list_schema.dump(battle.get_entries(count)).data)


class BattleVoting(Resource):
    def get(self, battle_id):
        """
        Get two entries to vote
        """
        battle = Battle.get_by_id(battle_id)
        if battle is None:
            abort(404, message="Battle could not not be found.")
        try:
            entry1, entry2 = battle.get_voting()
            return jsonify(entries_list_schema.dump([entry1, entry2]).data)
        except TypeError:
            abort(400, message="Couldn't get voting. Probably not enough entries in the git battle")

    @use_kwargs(vote_schema)
    def post(self, battle_id, voter_id, winner_id, loser_id):
        vote = Vote(voter_id=voter_id,
                    winner_id=winner_id,
                    loser_id=loser_id,
                    battle_id=battle_id)

        if try_add(vote):
            response = jsonify(vote_schema.dump(vote).data)
            response.status_code = 201
            return response
        else:
            abort(400, message="Couldn't create new vote")
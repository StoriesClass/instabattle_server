from flask import jsonify, request
from flask_restful import Resource, abort

from app import db
from app.api.common import BattleSchema
from app.api.common.validators import latitude_validator, longitude_validator
from app.helpers import try_add
from ...models import Battle, User
from ..common import battle_schema, battles_list_schema, entries_list_schema
from webargs import fields
from webargs.flaskparser import parser, use_args, use_kwargs


class BattlesListAPI(Resource):

    get_args = {
        'latitude': fields.Float(validate=latitude_validator),
        'longitude': fields.Float(validate=longitude_validator),
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
    def post(self, latitude, longitude, name, description, creator_id):
        """
        Create new battle
        :return: battle JSON if the battle was created
        """
        creator = User.get_by_id(creator_id)

        battle = Battle(latitude=latitude,
                        longitude=longitude,
                        name=name,
                        description=description,
                        creator=creator)

        if try_add(battle):
            return jsonify(battle_schema.dump(battle).data), 201
        else:
            abort(400, message="Couldn't create new battle")


class BattleAPI(Resource):
    def get(self, battle_id):
        """
        Get existing battle
        :return: battle info in JSON format
        """
        battle = Battle.get_by_id(battle_id)
        if battle is None:
            abort(400, message="Battle could not be found.")
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


class BattleEntries(Resource):
    def get(self, battle_id):
        """
        Get all entries of the battle
        """
        battle = Battle.get_by_id(battle_id)
        if battle is None:
            abort(404, message="Battle could not be found.")
        return jsonify(entries_list_schema.dump(battle.get_entries()).data)


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

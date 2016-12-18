from flask import jsonify, request
from flask_restful import Resource, abort
from marshmallow import validate
from webargs import fields
from webargs.flaskparser import use_kwargs

from app.helpers import try_add
from ...models import Entry, User, Battle
from ..common import entry_schema, entries_list_schema


class EntriesListAPI(Resource): # FIXME move to battle/id/entries
    @use_kwargs({'count': fields.Int(validate=validate.Range(min=1))})
    def get(self, count):
        # FIXME not top atm
        """
        Get all entries
        :return: list of top entries
        """
        entries = Entry.get_list(count)
        return jsonify(entries_list_schema.dump(entries).data)

    @use_kwargs(entry_schema)
    def post(self, latitude, longitude, user_id, battle_id):
        """
        Create new entry
        """
        user = User.query.get_or_404(user_id)
        battle = Battle.query.get_or_404(battle_id)
        entry = Entry(latitude=latitude,
                      longitude=longitude,
                      user=user,
                      battle=battle,
                      image=bytes(1024)) # FIXME

        if try_add(entry):
            return jsonify(entry_schema.dump(entry).data)
        else:
            abort(400, message="Couldn't create new entry")


class EntryAPI(Resource):
    def get(self, entry_id):
        """
        Get the entry
        """
        entry = Entry.get_by_id(entry_id)
        if entry is None:
            abort(400, message="Entry could not be found.")
        return jsonify(entry_schema.dump(entry).data)

    def put(self, entry_id):
        """
        Update the entry
        """ # FIXME
        entry = Entry.query.get_or_404(entry_id)
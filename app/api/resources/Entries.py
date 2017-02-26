from sqlite3 import IntegrityError

from flask import Response
from flask import jsonify
from flask_restful import Resource, abort
from marshmallow import validate
from webargs import fields
from webargs.flaskparser import use_kwargs

from app import db
from app.helpers import try_add
from ..common import entry_schema, entries_list_schema
from ...models import Entry, User, Battle


class EntriesListAPI(Resource): # FIXME move to battle/id/entries
    @use_kwargs({'count': fields.Int(validate=validate.Range(min=1))})
    def get(self, count):
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
                      battle=battle)

        if try_add(entry):
            response = jsonify(entry_schema.dump(entry).data)
            response.status_code = 201
            return response
        else:
            abort(400, message="Couldn't create new entry")

        # FIXME
        @use_kwargs({'entry_id': fields.Int()})
        def delete(self, entry_id):
            """
            Delete entry by id.
            :return: deleted entry if delete was successful
            """

            Entry.query.get_or_404(entry_id)
            Entry.query.filter_by(id=entry_id).delete()
            try:
                db.session.commit()
                return Response(status=204)
            except IntegrityError as e:
                print(e)
                abort(500, message="Entry exists but we couldn't delete it")


class EntryAPI(Resource):
    def get(self, entry_id):
        """
        Get the entry
        """
        entry = Entry.query.get_or_404(entry_id)
        return jsonify(entry_schema.dump(entry).data)

    def put(self, entry_id):
        """
        Update the entry
        """ # FIXME
        entry = Entry.query.get_or_404(entry_id)
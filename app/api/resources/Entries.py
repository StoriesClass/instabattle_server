from flask import jsonify
from flask_restful import Resource, abort
from ...models import Entry
from ..common import entry_schema


class EntriesListAPI(Resource):
    def post(self):
        """
        Create new entry
        """
        pass


class EntryAPI(Resource):
    def get(self, entry_id):
        """
        Get the entry
        """
        entry = Entry.get_by_id(entry_id)
        if entry is None:
            abort(400, message="Entry could not be found.")
        return jsonify({"entry": entry_schema.dump(entry).data})

    def put(self, entry_id):
        """
        Update the entry
        """
        pass

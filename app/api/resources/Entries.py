from flask_restful import Resource
from ...models import Entry


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
        pass

    def put(self, entry_id):
        """
        Update the entry
        """
        pass

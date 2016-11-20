from flask_restful import Resource


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
        pass

    def put(self, entry_id):
        """
        Update the entry
        """
        pass

from flask_restful import Resource


class UsersListAPI(Resource):
    def post(self):
        """
        Create new user
        """
        pass


class UsersTop(Resource):
    def get(self):
        """
        Get users top
        """
        pass


class UserAPI(Resource):
    def get(self, user_id):
        """
        Get existing user
        """
        pass

    def put(self, user_id):
        """
        Update user profile
        """
        pass


class UserResetPassword(Resource):
    def post(self, user_id):
        """
        Send to the user email to reset password
        """
        pass


class UserEntries(Resource):
    def get(self, user_id):
        """
        Get all battle entries of the user
        """
        pass

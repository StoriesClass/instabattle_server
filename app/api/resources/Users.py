from flask_restful import Resource
from ...models import User
from sqlalchemy.orm.exc import NoResultFound

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
        user = User.get_by_id(user_id)

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
        user = User.query.filter_by(id=user_id).one()

from flask_restful import Resource, abort
from ...models import User
from ..common import user_schema, users_list_schema
from flask import jsonify, request
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
        count = request.args.get('count', type=int)
        users = User.get_list(count)
        return jsonify({"users": users_list_schema.dump(users).data})


class UserAPI(Resource):
    def get(self, user_id):
        """
        Get existing user
        """
        user = User.get_by_id(user_id)
        if user is None:
            abort(400, message="User could not be found.")
        return jsonify({"user": user_schema.dump(user).data})


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
        user = User.get_by_id(user_id)

from flask_restful import Resource, abort, reqparse
from sqlalchemy.exc import IntegrityError

from app import db
from ...models import User
from ..common import user_schema, users_list_schema
from flask import jsonify, request


class UsersListAPI(Resource):
    def post(self):
        """
        Create new user
        """
        username = request.headers.get('username', type=str)
        email = request.headers.get('email', type=str)
        password = request.headers.get('password', type=str)
        if username and email and password:
            user = User(username=username,
                        email=email,
                        password=password)
            db.session.add(user)
            try:
                db.session.commit()
                user = db.session.refresh(user)
                return jsonify(user_schema.dump(user).data)
            except IntegrityError:
                db.session.rollback()
                abort(400, message="Could not create user")
        else:
            abort(400, message="Provide enough data")


class UsersTop(Resource):
    def get(self):
        """
        Get users top
        """
        count = request.args.get('count', type=int)
        users = User.get_list(count)
        return jsonify(users_list_schema.dump(users).data)


class UserAPI(Resource):
    def get(self, user_id):
        """
        Get existing user
        """
        user = User.get_by_id(user_id)
        if user is None:
            abort(400, message="User could not be found.")
        return jsonify(user_schema.dump(user).data)


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

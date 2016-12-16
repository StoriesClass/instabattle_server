from flask_restful import Resource, abort, reqparse
from marshmallow import validate
from sqlalchemy.exc import IntegrityError
from webargs import fields
from webargs.flaskparser import use_kwargs

from app import db
from app.helpers import try_add
from ...models import User
from ..common import user_schema, users_list_schema, entries_list_schema
from flask import jsonify, request


class UsersListAPI(Resource):
    @use_kwargs(user_schema)
    def post(self, username, email, password):
        """
        Create new user
        :return: battle JSON if the user was created
        """
        user = User(username=username,
                    email=email,
                    password=password)

        if try_add(user):
            return jsonify(user_schema.dump(user).data)
        else:
            abort(400, message="Couldn't create new user")

    @use_kwargs({'count': fields.Int(validate=validate.Range(min=1))})
    def get(self, count):
        # FIXME rating system?
        """
        Get users top
        :return: list of top users
        """
        users = User.get_list(count)
        return jsonify(users_list_schema.dump(users).data)


class UserAPI(Resource):
    def get(self, user_id):
        """
        Get existing user
        :return: user
        """
        user = User.get_by_id(user_id)

        if user is None:
            abort(404, message="User could not be found.")
        return jsonify(user_schema.dump(user).data)


    @use_kwargs(user_schema)
    def put(self, user_id, email, password, **kwargs):
        """
        Update user profile
        """
        user = User.query.get_or_404(user_id) # FIXME test
        if email:
            user.email = email
        if password:
            user.password = password

        if try_add(user):
            return jsonify(user_schema.dump(user).data)
        else:
            abort(400, message="Couldn't change user info")



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
        user = User.query.get_or_404(user_id)
        return jsonify(entries_list_schema.dump(user.get_entries()).data)

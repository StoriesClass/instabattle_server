from flask_restful import Resource, abort, reqparse
from marshmallow import validate
from sqlalchemy.exc import IntegrityError
from webargs import fields
from webargs.flaskparser import use_kwargs, use_args

from app import db
from app.api.common import UserSchema
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
            print(user_schema.dump(user).data)
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
    def get(self, user_id=None, username=None):
        """
        Get existing user
        :return: User
        """
        user = User.get_or_404(user_id, username)

        return jsonify(user_schema.dump(user).data)

    @use_kwargs(user_schema.factory)
    def put(self, email, password, user_id=None, username=None, **kwargs):
        """
        Update user profile
        :return: User
        """
        user = User.get_or_404(user_id, username)

        if email:
            user.email = email
        if password:
            user.password = password

        if try_add(user):
            return jsonify(user_schema.dump(user).data)
        else:
            abort(400, message="Couldn't change user info")

    def delete(self, user_id=None, username=None):
        """
        Delete user.
        :param user_id:
        :return: deleted user if delete was successful
        """
        if username:
            user_query = User.query.filter_by(username=username)
        elif user_id:
            user_query = User.query.filter_by(id=user_id)
        else:
            abort(404, message="Provide username or id")

        user = user_query.first_or_404()
        user_query.delete()
        try:
            db.session.commit()
            return jsonify(user_schema.dump(user).data)
        except IntegrityError as e:
            print(e)
            abort(500, message="User exists but we couldn't delete it")


class UserResetPassword(Resource):
    def post(self, user_id=None, username=None):
        """
        Send to the user email to reset password
        """
        user = User.get(user_id, username)


class UserEntries(Resource):
    def get(self, user_id=None, username=None):
        """
        Get all battle entries of the user
        """
        user = User.get_or_404(user_id, username)
        return jsonify(entries_list_schema.dump(user.get_entries()).data)

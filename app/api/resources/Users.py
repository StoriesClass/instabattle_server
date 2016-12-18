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
    def get(self, username):
        """
        Get existing user
        :return: user
        """
        user = User.query.filter_by(username=username).first_or_404()

        return jsonify(user_schema.dump(user).data)

    @use_kwargs(user_schema.factory)
    def put(self, username, email, password, **kwargs):
        """
        Update user profile
        """
        if not username:
            abort(400, message="Provide username")
        user = User.query.filter_by(username=username).first_or_404() # FIXME test
        if email:
            user.email = email
        if password:
            user.password = password

        if try_add(user):
            return jsonify(user_schema.dump(user).data)
        else:
            abort(400, message="Couldn't change user info")

    def delete(self, username):
        """
        Delete user.
        :param user_id:
        :return: deleted user if delete was successful
        """
        print(username)
        user_query = User.query.filter_by(username=username)
        user = user_query.first_or_404()
        user_query.delete()
        try:
            db.session.commit()
            return jsonify(user_schema.dump(user).data)
        except IntegrityError as e:
            print(e)
            abort(500, message="User exists but we couldn't delete it")


class UserResetPassword(Resource):
    def post(self, username):
        """
        Send to the user email to reset password
        """
        pass


class UserEntries(Resource):
    def get(self, username):
        """
        Get all battle entries of the user
        """
        user = User.query.filter_by(username=username).first_or_404()
        return jsonify(entries_list_schema.dump(user.get_entries()).data)

from flask import Response
from flask import jsonify
from flask_restful import Resource, abort
from marshmallow import validate
from sqlalchemy.exc import IntegrityError
from webargs import fields
from webargs.flaskparser import use_kwargs
from app import db
from app.api.authentication import not_anonymous_required
from app.api.common import UserSchema, votes_list_schema
from app.helpers import try_add
from ..common import user_schema, users_list_schema, entries_list_schema
from ...models import User


class UsersListAPI(Resource):
    @use_kwargs(user_schema)
    def post(self, username, email, password):
        """
        Create new user.
        :return: User or 400
        """
        user = User(username=username,
                    email=email,
                    password=password)

        if try_add(user):
            response = jsonify(user_schema.dump(user))
            response.status_code = 201
            return response
        else:
            abort(400, message="Couldn't create new user")

    @use_kwargs({'count': fields.Int(validate=validate.Range(min=1))})
    def get(self, count):
        """
        Get users top.
        :return: list of top users
        """
        users = User.get_list(count)
        return jsonify(users_list_schema.dump(users))


class UserAPI(Resource):
    def get(self, user_id=None, username=None):
        """
        Get existing user
        :return: User
        """
        user = User.get_or_404(user_id, username)

        return jsonify(user_schema.dump(user))

    @not_anonymous_required
    @use_kwargs(UserSchema(exclude=('username',), partial=('email',)))
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
            return jsonify(user_schema.dump(user))
        else:
            abort(400, message="Couldn't change user info")

    @not_anonymous_required
    def delete(self, user_id=None, username=None):
        """
        Delete user
        :return: deleted user if delete was successful
        """
        if username:
            user_query = User.query.filter_by(username=username)
        elif user_id:
            user_query = User.query.filter_by(id=user_id)
        else:
            abort(404, message="Provide username or id")
            return

        user_query.first_or_404()
        user_query.delete()
        try:
            db.session.commit()
            return Response(status=204)
        except IntegrityError:
            abort(500, message="User exists but we couldn't delete it")


class UserResetPassword(Resource):
    @not_anonymous_required
    def post(self, user_id=None, username=None):
        """
        Send to email to the user with reset password instructions
        """
        user = User.get_or_404(user_id, username)
        # TODO implement it


class UserEntries(Resource):
    def get(self, user_id=None, username=None):
        """
        Get all battle entries of the user
        """
        user = User.get_or_404(user_id, username)
        return jsonify(entries_list_schema.dump(user.entries))


class UserVotes(Resource):
    def get(self, user_id=None, username=None):
        """
        Get all votes of the user
        """
        user = User.get_or_404(user_id, username)
        return jsonify(votes_list_schema.dump(user.votes))

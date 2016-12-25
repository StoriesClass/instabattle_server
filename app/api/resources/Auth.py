from flask import g, jsonify
from flask_restful import Resource

from app.api.errors import unauthorized
from ..authentication import not_anonymous_required


class TokenAPI(Resource):
    @not_anonymous_required
    def get(self):
        """
        Get token
        """
        if g.current_user.is_anonymous or g.token_used:
            return unauthorized('Invalid credentials')
        return jsonify({'token':
                        g.current_user.generate_auth_token(expiration=3600),
                        'expiration': 3600})

class SignInAPI(Resource):
    def get(self):
        """

        :return:
        """
from flask_restful import Resource
from flask import g, jsonify
from ..common.errors import unauthorized


class TokenAPI(Resource):
    def get(self):
        """
        Get token
        """
        if g.current_user.is_anonymous or g.token_used:
            return unauthorized('Invalid credentials')
        return jsonify({'token':
                        g.current_user.generate_auth_token(expiration=3600),
                        'expiration': 3600})

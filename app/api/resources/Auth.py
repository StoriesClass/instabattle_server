from flask import g, jsonify
from flask_restful import Resource, abort
from ..authentication import not_anonymous_required


class TokenAPI(Resource):
    @not_anonymous_required
    def get(self):
        """
        Get token
        """
        if g.current_user.is_anonymous or g.token_used:
            abort(401, message="Invalid credentials")
        return jsonify({'token': g.current_user.generate_auth_token(expiration=3600),
                        'expiration': 3600})
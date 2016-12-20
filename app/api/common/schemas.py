from marshmallow import Schema, fields, validate
from marshmallow import ValidationError
from marshmallow import post_load
from marshmallow import pre_load

from app.api.common.validators import exists_in_db
from app.models import Battle, Entry, User


class BattleSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(load_only=True, validate=exists_in_db("User"))
    user_id = fields.Integer(load_only=True) # FIXME validate
    creator_id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(missing='')
    created_on = fields.DateTime(dump_only=True)
    latitude = fields.Float(required=True, validate=validate.Range(-90, 90))
    longitude = fields.Float(required=True, validate=validate.Range(-180, 180))
    entry_count = fields.Method("get_entry_count", dump_only=True)
    radius = fields.Float(required=True)

    def get_entry_count(self, obj):
        # FIXME poor performance
        return len(Battle.get_by_id(obj.id).get_entries())


    @staticmethod
    def factory(request):
        only = request.args.get('fields', None)
        if request.method == 'PUT':
            partial = True

        return UserSchema(only=only, partial=partial, context={'request': request}, exclude=exclude)

    class Meta:
        strict = True  # For using schemas with webargs


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3))
    email = fields.Email(required=True, validate=validate.Email())
    password = fields.Str(load_only=True)
    created_on = fields.DateTime(dump_only=True)
    rating = fields.Float(dump_only=True, validate=validate.Range(0, 1000))

    class Meta:
        strict = True

    @staticmethod
    def factory(request):
        # Filter based on 'fields' query parameter
        only = request.args.get('fields', None)
        # Respect partial updates for PUT requests and exclude username
        if request.method == 'PUT':
            exclude=['username']
            partial = True

        # Add current request to the schema's context
        return UserSchema(only=only, partial=partial, context={'request': request}, exclude=exclude)


class EntrySchema(Schema):
    id = fields.Int(dump_only=True)
    latitude = fields.Float(required=True, validate=validate.Range(-90, 90))
    longitude = fields.Float(required=True, validate=validate.Range(-180, 180))
    created_on = fields.DateTime(dump_only=True)
    image = fields.Str(dump_only=True)
    user_id = fields.Int(required=True)
    battle_id = fields.Int(required=True)
    rating = fields.Float(required=True, dump_only=True)

    @post_load
    def set_image(self, data):
        self.image = "{}_{}.jpg".format(data['battle_id'], data['user_id']) # FIXME temporary

    class Meta:
        strict = True


class VoteSchema(Schema):
    id = fields.Int(dump_only=True)
    created_on = fields.DateTime(dump_only=True)
    voter_id = fields.Int(required=True) # validate FIXME
    winner_id = fields.Int(required=True, validate=exists_in_db("Entry"))
    loser_id = fields.Int(required=True, validate=exists_in_db("Entry"))
    battle_id = fields.Int(dump_only=True, validate=exists_in_db("Battle"))

    @post_load
    def validate_entries_id(self, data):
        battle_id_winner = Entry.query.get(data['winner_id']).battle_id
        battle_id_loser = Entry.query.get(data['loser_id']).battle_id
        # validate with battle_id FIXME
        if not battle_id_winner == battle_id_loser:
            raise ValidationError("Both entries must be in chosen battle")

    class Meta:
        strict = True



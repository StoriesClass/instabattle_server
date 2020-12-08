from marshmallow import Schema, fields, validate
from marshmallow import ValidationError
from marshmallow import post_load

from app.api.common import custom_fields
from app.api.common.validators import exists_in_db
from app.models import Entry


class BattleSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(load_only=True, validate=exists_in_db("User"))
    user_id = fields.Int(load_only=True, validate=exists_in_db("User"))
    creator_id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(missing='')
    created_on = fields.DateTime(dump_only=True)
    latitude = fields.Float(required=True, validate=validate.Range(-90, 90))
    longitude = fields.Float(required=True, validate=validate.Range(-180, 180))
    entry_count = fields.Method("get_entry_count", dump_only=True)
    radius = fields.Float(required=True)


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = custom_fields.Lowercased(required=True, validate=(validate.Length(min=3), lambda x: x[0].isalpha()))
    email = fields.Email(required=True, validate=validate.Email())
    password = fields.Str(load_only=True)
    created_on = fields.DateTime(dump_only=True)
    rating = fields.Float(dump_only=True, validate=validate.Range(0, 1000))
    battle_creation_limit = fields.Int(dump_only=True)


class EntrySchema(Schema):
    id = fields.Int(dump_only=True)
    latitude = fields.Float(required=True, validate=validate.Range(-90, 90))
    longitude = fields.Float(required=True, validate=validate.Range(-180, 180))
    created_on = fields.DateTime(dump_only=True)
    image = fields.Str(dump_only=True)
    user_id = fields.Int(required=True, validate=exists_in_db("User"))
    battle_id = fields.Int(required=True, validate=exists_in_db("Battle"))
    rating = fields.Float(required=True, dump_only=True)


class VoteSchema(Schema):
    id = fields.Int(dump_only=True)
    created_on = fields.DateTime(dump_only=True)
    voter_id = fields.Int(required=True, validate=exists_in_db("User"))
    winner_id = fields.Int(required=True, validate=exists_in_db("Entry"))
    loser_id = fields.Int(required=True, validate=exists_in_db("Entry"))
    battle_id = fields.Int(dump_only=True, validate=exists_in_db("Battle"))

    @post_load
    def validate_schema(self, data):
        if data['winner_id'] == data['loser_id']:  # or \
            # User.is_voted(data['battle_id'], data['winner_id'], data['loser_id']): # FIXME
            raise ValidationError("Can't validate VoteSchema")

    @post_load  # FIXME
    def validate_entries_id(self, data):
        battle_id_winner = Entry.query.get(data['winner_id']).battle_id
        battle_id_loser = Entry.query.get(data['loser_id']).battle_id
        # validate with battle_id FIXME
        if not battle_id_winner == battle_id_loser:
            raise ValidationError("Both entries must be in chosen battle")

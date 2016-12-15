from marshmallow import Schema, fields, validate

from app.api.common.validators import latitude_validator, longitude_validator, exists_in_db
from app.models import Battle, Entry, User


class BattleSchema(Schema):
    id = fields.Int(dump_only=True)
    creator_id = fields.Int(required=True, validate=exists_in_db("User"))
    name = fields.Str(required=True)
    description = fields.Str(missing='')
    created_on = fields.DateTime(dump_only=True)
    latitude = fields.Float(required=True, validate=latitude_validator)
    longitude = fields.Float(required=True, validate=longitude_validator)
    entry_count = fields.Method("get_entry_count", dump_only=True)
    radius = fields.Float()

    def get_entry_count(self, obj):
        # FIXME poor performance
        return len(Battle.get_by_id(obj.id).get_entries())

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



class EntrySchema(Schema):
    id = fields.Int(dump_only=True)
    latitude = fields.Float(required=True, validate=latitude_validator)
    longitude = fields.Float(required=True, validate=longitude_validator)
    created_on = fields.DateTime(dump_only=True)
    image = fields.Str(dump_only=True)
    user_id = fields.Int(required=True)
    battle_id = fields.Int(required=True)
    rating = fields.Float(required=True, dump_only=True)

    class Meta:
        strict = True


class VoteSchema(Schema):
    id = fields.Int(dump_only=True)
    created_on = fields.DateTime(dump_only=True)
    voter_id = fields.Int(required=True, validate=exists_in_db("User"))
    entry_left_id = fields.Int(required=True, validate=exists_in_db("Entry"))
    entry_right_id = fields.Int(required=True, validate=exists_in_db("Entry"))
    battle_id = fields.Int(required=True, validate=exists_in_db("Battle"))
    chosen_entry = fields.Str(required=True,
                              validate=validate.OneOf(['left', 'right']))

    class Meta:
        strict = True



from marshmallow import Schema, fields


class BattleSchema(Schema):
    id = fields.Int()
    creator_id = fields.Int()
    name = fields.Str()
    description = fields.Str()
    created_on = fields.DateTime()
    latitude = fields.Float()
    longitude = fields.Float()


class EntrySchema(Schema):
    id = fields.Int()
    latitude = fields.Float()
    longitude = fields.Float()
    created_on = fields.DateTime()
    user_id = fields.Int()
    battle_id = fields.Int()
    rating = fields.Float()


class UserSchema(Schema):
    id = fields.Int()
    username = fields.Str()
    email = fields.Email()
    created_on = fields.DateTime()
    rating = fields.Float()
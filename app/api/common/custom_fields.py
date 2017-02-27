from marshmallow import fields


class Lowercased(fields.Field):
    def _serialize(self, value, attr, obj):
        if value is None:
            return ''
        return value.lower()
from webargs import ValidationError
from warnings import warn

from app.models import User, Battle, Entry, Vote


def user_exists_in_db(val):
    warn("deprecated, use exists_in_db instead", DeprecationWarning)
    if not User.get_by_id(val):
        raise ValidationError('User does not exist', status_code=404)


def battle_exists_in_db(val):
    warn("deprecated, use exists_in_db instead", DeprecationWarning)
    if not Battle.get_by_id(val):
        raise ValidationError('Battle does not exist', status_code=404)

def exists_in_db(cls_name):
    """
    Create validator for checking if the object exists in db.
    :param cls_name: Name of model which you want to validate
    :return: validator to use with marshmallow/webargs
    """
    cls = globals()[cls_name]
    def func(val):
        if not cls.get_by_id(val):
            raise ValidationError(cls.__name__ + ' does not exists', status_code=404)
    return func

def latitude_validator(l):
    if abs(l) > 90:
        raise ValidationError('Latitude is not in range [-90, 90]')

def longitude_validator(l):
    if abs(l) > 180:
        raise ValidationError('Longitude is not in range [-180, 180]')
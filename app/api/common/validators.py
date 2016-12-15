from webargs import ValidationError
from warnings import warn

def exists_in_db(cls_name):
    """
    Create validator for checking if the object exists in db.
    :param cls_name: Name of model which you want to validate
    :return: validator to use with marshmallow/webargs
    """
    from app.models import User, Battle, Entry, Vote
    cls = locals()[cls_name]
    def func(val):
        if not cls.get_by_id(val):
            raise ValidationError(cls.__name__ + ' does not exists', status_code=404)
    return func

def latitude_validator(l):
    warn("Deprecated, use validate.Range", DeprecationWarning)
    if abs(l) > 90:
        raise ValidationError('Latitude is not in range [-90, 90]')

def longitude_validator(l):
    warn("Deprecated, use validate.Range", DeprecationWarning)
    if abs(l) > 180:
        raise ValidationError('Longitude is not in range [-180, 180]')
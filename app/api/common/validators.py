from webargs import ValidationError


def exists_in_db(cls_name):
    """
    Create validator for checking if the object exists in db.
    :param cls_name: Name of a model which you want to validate
    :return: validator to use with marshmallow/webargs
    """
    # noinspection PyUnresolvedReferences
    from app.models import User, Battle, Entry, Vote
    cls = locals()[cls_name]

    def func(val):
        if not cls.query.get(val) and not \
                (cls_name == "User" and cls.query.filter_by(username=val).first()):
            raise ValidationError(cls_name + ' does not exists', status_code=404)

    return func

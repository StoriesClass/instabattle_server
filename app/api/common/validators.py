from webargs import ValidationError

def exists_in_db(cls_name):
    """
    Create validator for checking if the object exists in db.
    :param cls_name: Name of model which you want to validate
    :return: validator to use with marshmallow/webargs
    """
    from app.models import User, Battle, Entry, Vote
    cls = locals()[cls_name]
    def func(val):
        print("Validating ", val , " for ", cls_name)
        if cls_name == "User":
            if not cls.query.filter_by(username=val).first():
                raise ValidationError(cls_name + ' does not exists', status_code=404)
        else:
            if not cls.get_by_id(val):
                raise ValidationError(cls_name + ' does not exists', status_code=404)
    return func

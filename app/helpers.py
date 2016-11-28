from sqlalchemy.exc import IntegrityError
from . import db


def try_add(*objects):
    """
    Update database.
    :param objects: updated models
    :return: True if adding was successful, false otherwise
    """
    for obj in objects:
        db.session.add(obj)
    try:
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False
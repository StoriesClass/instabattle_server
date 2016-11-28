from sqlalchemy.exc import IntegrityError
from . import db

def try_add(obj):
    db.session.add(obj)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
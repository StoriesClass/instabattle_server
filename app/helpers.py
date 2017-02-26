import random

import forgery_py
from sqlalchemy.exc import IntegrityError

from . import db


def try_add(*objects):
    """
    Update database.
    :param objects: updated models
    :return: True if adding was successful, false otherwise
    """
    objects = filter(lambda x: x is not None, objects)
    db.session.add_all(objects)
    try:
        db.session.commit()
        return True
    except IntegrityError as e:
        print(e)
        db.session.rollback()
        return False


def generate_fake_user(**kwargs):
    from .models import User
    return User(email=kwargs.get('email', forgery_py.internet.email_address()),
                username=kwargs.get('username', forgery_py.internet.user_name(True)),
                password=kwargs.get('password', forgery_py.lorem_ipsum.word()))


def generate_fake_battle(**kwargs):
    from .models import Battle, User
    return Battle(created_on=forgery_py.date.datetime(past=True),
                  latitude=kwargs.get('password', forgery_py.geo.latitude()),
                  longitude=kwargs.get('longitude', forgery_py.geo.longitude()),
                  name=kwargs.get('name', forgery_py.lorem_ipsum.word()),
                  description=kwargs.get('description', forgery_py.lorem_ipsum.paragraph()),
                  creator=kwargs.get('creator') or random.choice(User.query.all()))


def generate_fake_entry(**kwargs):
    from .models import Entry, User, Battle
    return Entry(created_on=kwargs.get('created_on', forgery_py.date.datetime(past=True)),
                 latitude=kwargs.get('latitude', forgery_py.geo.latitude()),
                 longitude=kwargs.get('longitude', forgery_py.geo.longitude()),
                 user=kwargs.get('user') or random.choice(User.query.all()),
                 battle=kwargs.get('battle') or random.choice(Battle.query.all()))


def generate_fake_vote(**kwargs):
    from .models import Vote, User, Battle
    battle = random.choice(Battle.get_list())
    entries = battle.get_entries()
    if len(entries) < 2:
        return None
    id1 = random.choice(battle.get_entries()).id
    id2 = random.choice(battle.get_entries()).id
    while id1 == id2:
        id1 = random.choice(battle.get_entries()).id
        id2 = random.choice(battle.get_entries()).id
    return Vote(created_on=kwargs.get('created_on', forgery_py.date.datetime(past=True)),
                voter=kwargs.get('voter') or random.choice(User.query.all()),
                winner_id=kwargs.get('entry_left_id', id1),
                loser_id=kwargs.get('entry_right_id', id2),
                battle=kwargs.get('battle', battle))
#!/usr/bin/env python
import os
import random

from app import create_app, db
from flask_script import Manager, Shell
from app.models import User, Battle, Entry, Vote
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.environ.get('FLASK_CONFIG'))
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    """
    Create shell context for convenient debugging
    """
    return dict(db=db,
                app=app,
                User=User,
                Battle=Battle,
                Vote=Vote,
                Entry=Entry)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)


@manager.command
def test():
    """
    Run tests
    """
    import unittest
    loader = unittest.TestLoader()
    tests = loader.discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

@manager.command
def generate_fake(user_count=10, battle_count=10, entry_count=10, vote_count=10):
    """
    Generate fake users and battles
    :param user_count: Number of fake users.
    :param battle_count: Number of fake battles.
    :return: Nothing
    """
    from sqlalchemy.exc import IntegrityError
    from random import seed
    from os import urandom
    import forgery_py

    def try_add(obj):
        db.session.add(obj)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

    seed()
    for i in range(user_count):
        try_add(User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word()))

    # Because there is a small chance of collisions
    user_count = len(User.query.all())
    print("User count is", user_count)

    for i in range(battle_count):
        try_add(Battle(creation_datetime=forgery_py.date.datetime(past=True),
                       latitude=forgery_py.geo.latitude(),
                       longitude=forgery_py.geo.longitude(),
                       name=forgery_py.lorem_ipsum.word(),
                       description=forgery_py.lorem_ipsum.paragraph()))

    battle_count = len(Battle.query.all())
    print("Battle count is", battle_count)

    for i in range(entry_count):
        try_add(Entry(creation_datetime=forgery_py.date.datetime(past=True),
                      latitude=forgery_py.geo.latitude(),
                      longitude=forgery_py.geo.longitude(),
                      user_id=forgery_py.basic.number(at_most=user_count),
                      battle_id=forgery_py.basic.number(at_most=battle_count),
                      image=urandom(1024), # FIXME temporary
                      ))

    entry_count = len(Entry.query.all())
    print("Entry count is", entry_count)

    for i in range(vote_count):
        try_add(Vote(creation_datetime=forgery_py.date.datetime(past=True),
                     voter_id=forgery_py.basic.number(at_most=user_count),
                     entry_left_id=forgery_py.basic.number(at_most=entry_count),
                     entry_right_id=forgery_py.basic.number(at_most=entry_count),
                     battle_id=forgery_py.basic.number(at_most=battle_count),
                     chosen_entry=random.choice(['left', 'right'])))

    vote_count = len(Entry.query.all())
    print("Vote count is", vote_count)



if __name__ == '__main__':
    manager.run()

#!/usr/bin/env python
import os
import random

from app import create_app, db
from flask_script import Manager, Shell
from app.models import User, Battle, Entry, Vote
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.environ.get('FLASK_CONFIG') or 'testing')
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
def test(test=None):
    """
    Run tests
    """
    import unittest
    loader = unittest.TestLoader()
    if test:
        loader.testMethodPrefix = "test_" + test
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
    from random import seed
    from app.helpers import (try_add, generate_fake_user, generate_fake_battle,
                             generate_fake_entry, generate_fake_vote)

    seed()
    for i in range(user_count):
        user = generate_fake_user()
        if user:
            try_add(user)

    # Because there is a small chance of collisions
    user_count = len(User.query.all())
    print("User count is", user_count)

    for i in range(battle_count):
        battle = generate_fake_battle()
        if battle:
            try_add(battle)

    battle_count = len(Battle.query.all())
    print("Battle count is", battle_count)

    for i in range(entry_count):
        entry = generate_fake_entry()
        if entry:
            try_add(entry)

    entry_count = len(Entry.query.all())
    print("Entry count is", entry_count)

    for i in range(vote_count):
        vote = generate_fake_vote()
        if vote:
            try_add(vote)

    vote_count = len(Entry.query.all())
    print("Vote count is", vote_count)


if __name__ == '__main__':
    manager.run()

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
    from app.helpers import (generate_fake_user, generate_fake_battle,
                             generate_fake_entry,generate_fake_vote)
    from app.helpers import try_add
    return dict(db=db,
                app=app,
                User=User,
                Battle=Battle,
                Vote=Vote,
                Entry=Entry,
                fake_user=generate_fake_user,
                fake_battle=generate_fake_battle,
                fake_entry=generate_fake_entry,
                fake_vote=generate_fake_vote,
                try_add=try_add)


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
def deploy():
    """
    Deploy command. Normally called by initialization scripts on hosting.
    """
    from flask_migrate import upgrade

    upgrade()


@manager.command
def generate_fake(user_count=7, battle_count=21, entry_count=100, vote_count=200):
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
    try_add(*(generate_fake_user() for _ in range(user_count)))

    # Because there is a small chance of collisions
    user_count = len(User.query.all())
    print("User count is", user_count)

    try_add(*(generate_fake_battle() for _ in range(battle_count)))

    battle_count = len(Battle.get_list())
    print("Battle count is", battle_count)

    try_add(*(generate_fake_entry() for _ in range(entry_count)))

    entry_count = len(Entry.get_list())
    print("Entry count is", entry_count)

    try_add(*(generate_fake_vote() for _ in range(vote_count)))

    vote_count = len(Vote.query.all())
    print("Vote count is", vote_count)


if __name__ == '__main__':
    manager.run()

#!/usr/bin/env python
import os

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


if __name__ == '__main__':
    manager.run()
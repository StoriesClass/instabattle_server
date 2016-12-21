import os
import unittest

from pyresttest import resttest
from app import create_app, db
from app.helpers import try_add, generate_fake_user
from app.models import User


class DeclarativeTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        users = [generate_fake_user(username="creator",
                                    email="creator@instabattle.me",password="123"),
                 generate_fake_user(username="voter1"),
                 generate_fake_user(username="voter2")]
        if not try_add(*users):
            self.fail("Couldn't create users in SetUp")
        print(User.query.get(1))


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def declarative_tester(self, name):
        # FIXME Travis CI and logging
        with self.assertRaises(SystemExit) as failures:
            resttest.main({'url': "http://localhost:8000", 'test': 'tests/test_' + name + '.yaml'})
        self.assertEqual(failures.exception.code, 0)

    def test_declarative_battle(self):
        self.declarative_tester(name="battle")

    def test_declarative_user(self):
        self.declarative_tester(name="user")

    def test_declarative_auth(self):
        self.declarative_tester(name="auth")

    def test_declarative_entry(self):
        self.declarative_tester(name="entry")
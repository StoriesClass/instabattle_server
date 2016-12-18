import os
import unittest

from pyresttest import resttest
from app import create_app, db
from app.helpers import try_add, generate_fake_user
from app.models import User


class YAMLTestCase(unittest.TestCase):
    def setUp(self):
        print("SET UP")
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        if not try_add(generate_fake_user(username="creator")):
            self.fail("Couldn't create user 'creator'")
        print(User.query.get(1))


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_yaml_all(self, name="all"):
        # FIXME Travis CI and logging
        with self.assertRaises(SystemExit) as failures:
            resttest.main({'url': "http://localhost:8000", 'test': 'tests/test_' + name + '.yaml'})
        self.assertEqual(failures.exception.code, 0)

    def test_yaml_battle(self):
        self.test_yaml_all(name="battle")

    def test_yaml_user(self):
        self.test_yaml_all(name="user")
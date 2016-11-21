import unittest
from app import create_app, db
from app.models import Battle


class BattleModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_in_radius(self):
        self.assertTrue(True)  # FIXME

    def test_get_all(self):
        battles = Battle.get_all()
        self.assertEquals(0, len(battles))
        size = 10
        for b in (Battle(name="Battle" + str(i)) for i in range(size)):
            db.session.add(b)
        db.session.commit()
        battles = Battle.get_all()
        self.assertEquals(size, len(battles))
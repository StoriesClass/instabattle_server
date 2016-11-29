import unittest
from app import create_app, db
from app.models import Battle, User, Entry, Vote


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

    def test_get_list(self):
        battles = Battle.get_list()
        self.assertEquals(0, len(battles))
        size = 10
        for b in (Battle(name="Battle" + str(i)) for i in range(size)):
            db.session.add(b)
        db.session.commit()
        battles = Battle.get_list()
        self.assertEquals(size, len(battles))

    def test_voting(self):
        from app.helpers import (generate_fake_entry, generate_fake_vote,
                                   generate_fake_user, generate_fake_battle)
        voter = generate_fake_user()
        u_left = generate_fake_user()
        u_right = generate_fake_user()
        creator = generate_fake_user()
        b = generate_fake_battle(creator=creator)
        e_left = generate_fake_entry(user=u_left, battle=b)
        e_right = generate_fake_entry(user=u_right, battle=b)
        db.session.add_all((b, voter, u_left, u_right, e_left, e_right))
        db.session.flush()
        db.session.refresh(e_left)
        db.session.refresh(e_right)
        v = generate_fake_vote(voter=voter,
                               entry_left_id=e_left.id,
                               entry_right_id=e_right.id,
                               battle=b,
                               chosen_entry='left')
        db.session.add(v)
        db.session.commit()
        self.assertGreater(e_left.rating, e_right.rating)
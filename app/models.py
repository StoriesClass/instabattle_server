from werkzeug.security import generate_password_hash, check_password_hash
from . import db


class Vote(db.Model):
    __tablename__ = 'votes'
    id = db.Column(db.Integer, primary_key=True)
    creation_datetime = db.Column(db.DateTime)
    voter_id = db.Column(db.Integer,
                        db.ForeignKey('users.id'))
    entry_left_id = db.Column(db.Integer,
                          db.ForeignKey('entries.id'))
    entry_right_id = db.Column(db.Integer,
                             db.ForeignKey('entries.id'))
    battle_id = db.Column(db.Integer,
                          db.ForeignKey('battles.id'))

    chosen_entry = db.Column(db.Enum('left', 'right'))

    def __repr__(self):
        return "<Vote by {} in battle {}>".format(self.user_id, self.battle_id)


class Entry(db.Model):
    __tablename__ = 'entries'
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    creation_datetime = db.Column(db.DateTime)
    image = db.Column(db.LargeBinary)

    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id'))
    battle_id = db.Column(db.Integer,
                          db.ForeignKey('battles.id'))


    def __repr__(self):
        return "<Entry of {} in battle {}>".format(self.user_id, self.battle_id)


class Battle(db.Model):
    __tablename__ = 'battles'
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer,
                           db.ForeignKey('users.id'),
                           index=True)
    name = db.Column(db.String(64), index=True)
    description = db.Column(db.String(1024))
    creation_datetime = db.Column(db.DateTime)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)


    entries = db.relationship('Entry',
                              backref='battle',
                              lazy='dynamic',
                              cascade='all, delete-orphan')

    votes = db.relationship('Vote',
                            backref='battle',
                            lazy='dynamic',  # FIXME what does it mean actually?
                            cascade='all, delete-orphan')

    # FIXME doesn't work properly
    @staticmethod
    def get_in_radius(latitude, longitude, radius):
        return db.session.query(Battle).filter(
            (latitude-Battle.latitude)**2 + (longitude-Battle.longitude)**2 <= radius**2)

    @staticmethod
    def get_all():
        """
        Get all battles. Only for debuggin purposes.
        :return: List of all battles in database.
        """
        return Battle.query.all()

    def get_votes(self):
        return self.entries.all()

    def get_entries(self):
        return self.entries.all()


    def __repr__(self):
        return "<Battle {}>".format(self.id)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    votes = db.relationship('Vote',
                            backref='user',
                            lazy='dynamic',  # FIXME what does it mean actually?
                            cascade='all, delete-orphan')

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def participate(self, battle):
        pass  # FIXME

    def __repr__(self):
        return "<User {}>".format(self.username)

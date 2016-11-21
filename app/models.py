from werkzeug.security import generate_password_hash, check_password_hash
from . import db


class Vote(db.Model):
    __tablename__ = 'votes'
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id'),
                        primary_key=True)
    battle_id = db.Column(db.Integer,
                          db.ForeignKey('battles.id'),
                          primary_key=True)

    def __repr__(self):
        return "<Vote by {} in battle {}>".format(self.user_id, self.battle_id)


class Entry(db.Model):
    __tablename__ = 'entries'
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id'),
                        primary_key=True)
    battle_id = db.Column(db.Integer,
                          db.ForeignKey('battles.id'),
                          primary_key=True)

    def __repr__(self):
        return "<Entry of {} in battle {}>".format(self.user_id, self.battle_id)


class Battle(db.Model):
    __tablename__ = 'battles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    description = db.Column(db.String(1024))
    creation_date = db.Column(db.DateTime)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    votes = db.relationship('Vote',
                            backref='battle',
                            lazy='dynamic',  # FIXME what does it mean actually?
                            cascade='all, delete-orphan')
    entries = db.relationship('Entry',
                              backref='battle',
                              lazy='dynamic',
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


    def __repr__(self):
        return "<Battle {}>".format(id)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)



    def __repr__(self):
        return "<User {}>".format(self.username)

from sqlalchemy import CheckConstraint, Index
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import desc, func
from sqlalchemy.ext.hybrid import hybrid_method


class Vote(db.Model):
    __tablename__ = 'votes'
    id = db.Column(db.Integer, primary_key=True)
    created_on = db.Column(db.DateTime, default=datetime.now,
                           onupdate=datetime.now)
    voter_id = db.Column(db.Integer,
                         db.ForeignKey('users.id'), nullable=False)
    voter = db.relationship('User', backref=db.backref('votes'))
    entry_left_id = db.Column(db.Integer,
                              db.ForeignKey('entries.id'), nullable=False)
    entry_right_id = db.Column(db.Integer,
                               db.ForeignKey('entries.id'), nullable=False)
    battle_id = db.Column(db.Integer,
                          db.ForeignKey('battles.id'), nullable=False)
    battle = db.relationship('Battle', uselist=False)

    chosen_entry = db.Column(db.Enum('left', 'right', name="side_enum",))

    def __repr__(self):
        return "<Vote by {} in battle {}>".format(self.user_id, self.battle_id)


class Entry(db.Model):
    __tablename__ = 'entries'

    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    created_on = db.Column(db.DateTime, default=datetime.now,
                           onupdate=datetime.now)
    image = db.Column(db.LargeBinary, nullable=False)

    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('entries'))
    battle_id = db.Column(db.Integer,
                          db.ForeignKey('battles.id'), nullable=False)
    battle = db.relationship('Battle', backref=db.backref('entries'))

    __table_args__ = (Index('ix_location', latitude, longitude),)

    @staticmethod
    def get_by_id(id):
        """
        :param id: identifier of the wanted entry.
        :return: Entry object if there is a battle with given id,
        None otherwise.
        """
        try:
            entry = Entry.query.filter_by(id=id).one()
        except NoResultFound:
            return None
        return entry

    @staticmethod
    def get_list(count=None):
        """
        Return all entries if count is not provided,
        otherwise only given number of entries.
        :param count: Number of entries to get.
        :return: List of Entry objects.
        """
        if count is None:
            entries = Entry.query.all()
        else:
            entries = Entry.query.limit(count)
        return entries

    def __repr__(self):
        return "<Entry of {} in battle {}>".format(self.user_id, self.battle_id)


class Battle(db.Model):
    __tablename__ = 'battles'
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer,
                           db.ForeignKey('users.id'),
                           index=True)
    creator = db.relationship('User', uselist=False)
    name = db.Column(db.String(64), index=True, nullable=False)
    description = db.Column(db.Text())
    created_on = db.Column(db.DateTime, default=datetime.now)
    latitude = db.Column(db.Float, CheckConstraint(
        '(-90 <= latitude) AND (latitude <= 90)'))
    longitude = db.Column(db.Float, CheckConstraint(
        '(-180 <= longitude) AND (longitude <= 180)'))

    # FIXME doesn't work properly
    @hybrid_method
    def distance_to(self, latitude, longitude):
        return (abs(self.latitude - latitude) / 90 +
                abs(self.longitude - longitude) / 180) / 2

    @distance_to.expression
    def distance_to(cls, latitude, longitude):
        return (func.abs(cls.latitude - latitude) / 90 +
                func.abs(cls.longitude - longitude) / 180) / 2

    @staticmethod
    def get_in_radius(latitude, longitude, radius):
        """
        Radius is metaphorical for now.
        :param latitude:
        :param longitude:
        :param radius: a value from 0 to 1 where 1 means whole map
        :return: Battles close to point with coordinates (latitude, longitude)
        according to some "magic" metric.
        """
        return db.session.query(Battle).filter(
            Battle.distance_to(latitude, longitude) < radius).all()

    @staticmethod
    def get_by_id(id):
        """
        :param id: identifier of the wanted battle.
        :return: Battle object if there is a battle with given id,
        None otherwise.
        """
        try:
            battle = Battle.query.filter_by(id=id).one()
        except NoResultFound:
            return None
        return battle

    @staticmethod
    def get_list(count=None):
        """
        Return all battles if count is not provided,
        otherwise only given number of battles.
        :param count: Number of battles to get.
        :return: List of Battle objects.
        """
        if count is None:
            battles = Battle.query.all()
        else:
            battles = Battle.query.limit(count)
        return battles

    def get_votes(self):
        """
        Get all votes of the battle.
        :return: List of Vote objects.
        """
        return self.votes

    def get_entries(self):
        """
        Get all entries of the battle.
        :return: List of Entry objects.
        """
        return self.entries

    def __repr__(self):
        return "<Battle {}>".format(self.id)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.now)
    password_hash = db.Column(db.String(128), nullable=False)
    rating = db.Column(db.Integer, default=1000, nullable=False)

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        """
        Securely set password.
        :param password:
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check if user's password matches with given.
        :param password:
        """
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_id(id):
        """
        :param id: identifier of the wanted user.
        :return: Entry object if there is a user with given id,
        None otherwise.
        """
        try:
            entry = Entry.query.filter_by(id=id).one()
        except NoResultFound:
            return None
        return entry

    @staticmethod
    def get_list(count=None):
        """
        Return all users if count is not provided,
        otherwise only given number of users.
        :param count: Number of battles to get.
        :return: List of User objects sorted by rating.
        """
        users = User.query.order_by(desc(User.rating))
        if count is None:
            users = users.all()
        else:
            users = users.limit(count)
        return users

    def __repr__(self):
        return "<User {}>".format(self.username)

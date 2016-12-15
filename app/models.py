import random

from flask import current_app
from sqlalchemy import CheckConstraint, Index
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin, login_manager
from . import db
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import desc, func
from sqlalchemy.ext.hybrid import hybrid_method
from trueskill import Rating, rate_1vs1, quality_1vs1
from .helpers import try_add
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class Permission:
    PARTICIPATE = 0x01
    VOTE = 0x02
    CREATE = 0x04
    APPROVE = 0x08
    MODERATE = 0x0f
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = (('User', Permission.PARTICIPATE | Permission.VOTE |
                  Permission.CREATE, True),
                 ('Moderator', Permission.PARTICIPATE | Permission.SUGGEST |
                  Permission.APPROVE, False), ('Administrator', 0xff, False))
        for name, permissions, default in roles:
            role = Role.query.filter_by(name=name).first()
            if not role:
                role = Role(name=name)
            role.permissions = permissions
            role.default = default
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return "<Role {}>".format(self.name)


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

    def __init__(self, *args, **kwargs):
        super(Vote, self).__init__(*args, **kwargs)
        entry_left = Entry.get_by_id(int(self.entry_left_id))
        entry_right = Entry.get_by_id(int(self.entry_right_id))
        rating_left = Rating(entry_left.get_rating())
        rating_right = Rating(entry_right.get_rating())
        new_rating_left, new_rating_right = rate_1vs1(rating_left, rating_right) if\
            self.chosen_entry == 'left' else rate_1vs1(rating_right, rating_left)
        entry_left.rating = float(new_rating_left)
        entry_right.rating = float(new_rating_right)
        try_add(entry_left, entry_right)

    def __repr__(self):
        return "<Vote by {} in battle {}>".format(self.voter_id, self.battle_id)


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
    rating = db.Column(db.Float, default=float(Rating()), nullable=False)

    __table_args__ = (Index('ix_location', latitude, longitude),)

    def get_rating(self):
        return self.rating

    @staticmethod
    def get_by_id(battle_id):
        """
        :param battle_id: identifier of the wanted entry.
        :return: Entry object if there is a battle with given id,
        None otherwise.
        """
        try:
            entry = Entry.query.get(battle_id)
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
        if not count:
            entries = Entry.query.all()
        else:
            entries = Entry.query.limit(count).all()
        return entries

    def __repr__(self):
        return "<Entry {}  of user {} in battle {}>".format(self.id, self.user_id, self.battle_id)


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
        '(-90 <= latitude) AND (latitude <= 90)'), nullable=False)
    longitude = db.Column(db.Float, CheckConstraint(
        '(-180 <= longitude) AND (longitude <= 180)'), nullable=False)

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
    def get_by_id(battle_id):
        """
        :param battle_id: identifier of the wanted battle.
        :return: Battle object if there is a battle with given id,
        None otherwise.
        """
        try:
            battle = Battle.query.get(battle_id)
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
        if not count:
            battles = Battle.query.all()
        else:
            battles = Battle.query.limit(count).all()
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

    def get_voting(self):
        """
        Get two entries to vote using sophisticated algorithm.
        :return: Tuple of two entries if conditions are met. Otherwise false.
        """
        entries = self.get_entries()

        if len(entries) >= 2:
            entry1 = random.choice(entries)
            entry2 = random.choice(entries)
            rating1 = Rating(entry1.rating)
            rating2 = Rating(entry2.rating)
            impatience = 0
            while entry1 == entry2 or quality_1vs1(rating1, rating2) < 0.3 - impatience:
                entry1 = random.choice(entries)
                entry2 = random.choice(entries)
                impatience += 0.01
            return entry1, entry2
        return None

    def __repr__(self):
        return "<Battle {}>".format(self.id)


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.now)
    password_hash = db.Column(db.String(128), nullable=False)
    rating = db.Column(db.Float, default=float(Rating()), nullable=False)

    def __init__(self, *args, **kwargs):
        UserMixin.__init__(self)
        db.Model.__init__(self, *args, **kwargs)

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
    def get_by_id(entry_id):
        """
        :param id: identifier of the wanted user.
        :return: Entry object if there is a user with given id,
        None otherwise.
        """
        try:
            user = User.query.get(entry_id)
        except NoResultFound:
            return None
        return user

    def get_entries(self):
        return self.entries

    @staticmethod
    def get_list(count=None):
        """
        Return all users if count is not provided,
        otherwise only given number of users.
        :param count: Number of battles to get.
        :return: List of User objects sorted by rating.
        """
        users = User.query.order_by(desc(User.rating))
        if not count :
            users = users.all()
        else:
            users = users.limit(count).all()
        return users

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return "<User {}>".format(self.username)


class AnonymousUser(AnonymousUserMixin):
    pass

login_manager.anonymous_user = AnonymousUser

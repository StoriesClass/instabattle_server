import random
from flask import current_app
from flask_restful import abort
from sqlalchemy import CheckConstraint, Index
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin, login_manager
from . import db
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import desc
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
    voter = db.relationship('User', backref=db.backref('votes', cascade="all, delete-orphan"))
    winner_id = db.Column(db.Integer,
                          db.ForeignKey('entries.id'), nullable=False)
    loser_id = db.Column(db.Integer,
                         db.ForeignKey('entries.id'), nullable=False)
    battle_id = db.Column(db.Integer,
                          db.ForeignKey('battles.id'), nullable=False)
    battle = db.relationship('Battle', uselist=False)

    def __init__(self, *args, **kwargs):
        super(Vote, self).__init__(*args, **kwargs)
        winner = Entry.get_by_id(self.winner_id)
        loser = Entry.get_by_id(self.loser_id)
        rating_winner = winner.rating
        rating_loser = loser.rating
        new_rating_winner, new_rating_loser = rate_1vs1(rating_winner, rating_loser)
        winner.rating = new_rating_winner
        loser.rating = new_rating_loser
        try_add(winner, loser)

    def __repr__(self):
        return "<Vote by {} in battle {}>".format(self.voter_id, self.battle_id)


class Entry(db.Model):
    __tablename__ = 'entries'

    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    created_on = db.Column(db.DateTime, default=datetime.now,
                           onupdate=datetime.now)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('entries', cascade="all, delete-orphan"))
    battle_id = db.Column(db.Integer,
                          db.ForeignKey('battles.id'), nullable=False)
    battle = db.relationship('Battle', backref=db.backref('entries', cascade="all, delete-orphan"))
    _rating = db.Column('rating', db.Float, default=Rating().mu, nullable=False)
    rating_deviation = db.Column(db.Float, default=Rating().sigma, nullable=False)

    __table_args__ = (Index('ix_location', latitude, longitude),)

    @property
    def image(self):
        return '{}_{}_{}'.format(self.battle_id, self.user_id, self.id)

    @property
    def rating(self):
        return Rating(self._rating, self.rating_deviation)

    @rating.setter
    def rating(self, rating):
        self._rating = rating.mu
        self.rating_deviation = rating.sigma

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
        :return: List of Entry objects sorted by rating.
        """
        entries = Entry.query.order_by(desc(Entry._rating))
        if not count:
            entries = entries.all()
        else:
            entries = entries.limit(count).all()
        return entries

    def __repr__(self):
        return "<Entry {}  of user {} in battle {}>".format(self.id, self.user_id, self.battle_id)


class Battle(db.Model):
    __tablename__ = 'battles'
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer,
                           db.ForeignKey('users.id'),
                           index=True)
    creator = db.relationship('User', uselist=False, backref=db.backref("battles"))
    name = db.Column(db.String(64), index=True, nullable=False)
    description = db.Column(db.Text())
    created_on = db.Column(db.DateTime, default=datetime.now)
    latitude = db.Column(db.Float, CheckConstraint(
        '(-90 <= latitude) AND (latitude <= 90)'), nullable=False)
    longitude = db.Column(db.Float, CheckConstraint(
        '(-180 <= longitude) AND (longitude <= 180)'), nullable=False)
    radius = db.Column(db.Integer, nullable=False, server_default="100")  # FIXME no default

    @hybrid_method
    def distance_to(self, latitude, longitude):
        from haversine import haversine
        return haversine((latitude, longitude), (self.latitude, self.longitude))

    # @distance_to.expression
    # def distance_to(cls, latitude, longitude):
    #    return (func.abs(cls.latitude - latitude) / 90 +
    #            func.abs(cls.longitude - longitude) / 180) / 2

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

    def get_entries(self, count=None):
        """
        Get all entries of the battle.
        :return: List of Entry objects.
        """
        query = Entry.query.filter_by(battle_id=self.id).order_by(desc(Entry._rating))
        if count:
            return query.limit(count).all()
        else:
            return query.all()

    def get_voting(self, user_id):
        """
        Get two entries to vote using sophisticated algorithm.
        :return: Tuple of two entries if conditions are met. Otherwise false.
        """
        entries = [e for e in self.get_entries() if e.user_id != user_id]

        user = User.get_or_404(user_id=user_id)
        if len(entries) >= 2:
            entry1 = random.choice(entries)
            entry2 = random.choice(entries)
            rating1 = entry1.rating
            rating2 = entry2.rating
            impatience = 0
            while entry1.id == entry2.id or quality_1vs1(rating1, rating2) < 0.3 - impatience or \
                    (user.is_voted(entry1.battle_id, entry1.id, entry2.id) and impatience < 1):  # FIXME
                entry1 = random.choice(entries)
                entry2 = random.choice(entries)
                impatience += 0.01
            if not user.is_voted(entry1.battle_id, entry1.id, entry2.id) and not entry1.id == entry2.id:
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
    _rating = db.Column("rating", db.Float, default=Rating().mu, nullable=False)
    rating_deviation = db.Column(db.Float, default=Rating().sigma, nullable=False)

    def __init__(self, *args, **kwargs):
        UserMixin.__init__(self)
        db.Model.__init__(self, *args, **kwargs)

    @property
    def rating(self):
        return Rating(self._rating, self.rating_deviation)

    @rating.setter
    def rating(self, rating):
        self._rating = rating.mu
        self.rating_deviation = rating.sigma

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        """
        Securely set password.
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check if user's password matches with given.
        """
        return check_password_hash(self.password_hash, password)

    def is_voted(self, battle_id, winner_id, loser_id):
        return Vote.query.filter(
            (Vote.voter_id == self.id) &
            (Vote.battle_id == battle_id) & (
                ((Vote.winner_id == winner_id) & (Vote.loser_id == loser_id)) |
                ((Vote.winner_id == loser_id) & (Vote.loser_id == winner_id))
            )).count() != 0

    @property
    def battle_creation_limit(self):
        DAYS_TO_NEW_BATTLE = 7
        BATTLES_AT_START = 7

        extra_battles = (datetime.now() - self.created_on).days // DAYS_TO_NEW_BATTLE

        return BATTLES_AT_START - len(self.battles) + extra_battles

    @staticmethod
    def get_or_404(user_id=None, username=None, message=None):
        """
        :param user_id: identifier of the wanted user.
        :param username: name of the wanted user.
        :return: Entry object if there is a user with given id or username,
        404 otherwise.
        """
        if username:
            return User.query.filter_by(username=username).first_or_404()
        elif user_id:
            return User.query.get_or_404(user_id)
        else:
            abort(404, message=(message or "Provide username or id"))

    @staticmethod
    def get(user_id=None, username=None):
        """
        :param user_id: identifier of the wanted user.
        :param username: name of wanted user.
        :return: User object if there is a user with given id or username,
        None otherwise.
        """
        if username:
            return User.query.filter_by(username=username).first()
        elif user_id:
            return User.query.get(user_id)
        return None

    @staticmethod
    def get_list(count=None):
        """
        Return all users if count is not provided,
        otherwise only given number of users.
        :param count: Number of battles to get.
        :return: List of User objects sorted by rating.
        """
        users = User.query.order_by(desc(User._rating))
        if not count:
            return users.all()
        else:
            return users.limit(count).all()

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

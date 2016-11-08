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
    votes = db.relationship('Vote',
                            backref='battle',
                            lazy='dynamic',  # FIXME what does it mean actually?
                            cascade='all, delete-orphan')
    entries = db.relationship('Entry',
                              backref='battle',
                              lazy='dynamic',
                              cascade='all, delete-orphan')

    def __repr__(self):
        return "<Battle {}>".format(id)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return "<User {}>".format(self.username)

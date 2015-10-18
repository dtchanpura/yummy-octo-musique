from app import db
from constants import ALPHABET


class Song(db.Model):
    __tablename__ = "songs"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    # artist = db.Column(db.String(255))
    album = db.Column(db.String(255))
    album_artist = db.Column(db.String(255))
    composer = db.Column(db.String(255))
    # performer = db.Column(db.String(255))
    genre = db.Column(db.String(255))
    comments = db.Column(db.String(255))
    file_name = db.Column(db.String(1023))
    file_size = db.Column(db.BigInteger)
    length = db.Column(db.Integer)
    bit_rate = db.Column(db.Integer)
    sample_rate = db.Column(db.Integer)
    file_type = db.Column(db.String(16))

    def __init__(self, eyed3_meta=None):
        if eyed3_meta is not None:
            self.album = eyed3_meta.tag.album
            self.album_artist = eyed3_meta.tag.album_artist
            self.title = eyed3_meta.tag.title
        else:
            super(self)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    salt_string = db.Column(db.String)
    password = db.Column(db.String)
    token = db.Column(db.String, unique=True)

    def __init__(self, username, password):
        """
        :param username:
        :param password:
        :return:
        """

        import random
        import hashlib
        self.salt_string = ''.join(random.choice(ALPHABET) for i in range(16))
        self.username = username
        self.password = hashlib.sha256(password + self.salt_string).hexdigest()
        self.token = ''.join(random.choice(ALPHABET) for i in range(40))

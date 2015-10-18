from app import db
from constants import ALPHABET


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

from app import db

class Song(db.Model):
    __tablename__ = "songs"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    #artist = db.Column(db.String(255))
    album = db.Column(db.String(255))
    album_artist = db.Column(db.String(255))
    composer = db.Column(db.String(255))
    #performer = db.Column(db.String(255))
    genre = db.Column(db.String(255))
    comments = db.Column(db.String(255))
    file_name = db.Column(db.String(1023))
    file_size = db.Column(db.BigInteger)
    length = db.Column(db.Integer)
    bit_rate = db.Column(db.Integer)
    sample_rate = db.Column(db.Integer)
    file_type = db.Column(db.String(16))

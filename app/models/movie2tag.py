from .. import db

class Movie2Tag(db.Model):
    __tablename__ = 'movie2tag'
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'),
                        primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'),
                        primary_key=True)
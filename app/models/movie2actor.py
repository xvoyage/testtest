from .. import db

class Movie2Actor(db.Model):
    __tablename__ = 'movie2actor'
    actor_id = db.Column(db.Integer, db.ForeignKey('actors.id'),
                        primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'),
                        primary_key=True)   
from .. import db
# from .movie import Movie2Actor
from .movie2actor import Movie2Actor

class Actor(db.Model):
    __tablename__ = 'actors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    sortnum = db.Column(db.Integer)
    description = db.Column(db.Text)
    imgurl = db.Column(db.String(128))
    love = db.Column(db.Boolean, default=False)
    vides = db.relationship('Movie2Actor',
                            foreign_keys=[Movie2Actor.actor_id],
                            backref=db.backref('actors', lazy='joined'),
                            lazy='dynamic',
                            cascade='all, delete-orphan')


    def __repr__(self):
        return '<Actor %r>' %  self.name


    def check_name(self):
        if self.name is not None:
            c = Actor.query.filter_by(name=self.name).first()
            if not c:
                return True
        
        return False
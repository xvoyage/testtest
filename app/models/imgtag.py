from .. import db
# from .movie import Movie2Tag
# from .movie2tag import Movie2Tag
from .photo2tag import Photo2Tag

class ImgTag(db.Model):
    __tablename__ = 'imgtags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    sortnum = db.Column(db.Integer)
    photos = db.relationship('Photo2Tag',
                            foreign_keys=[Photo2Tag.tag_id],
                            backref=db.backref('tags', lazy='joined'),
                            lazy='dynamic',
                            cascade='all, delete-orphan')

    def __repr__(self):
        return '<Tag %r>' % self.name


    def check_name(self):
        if self.name is not None:
            c = ImgTag.query.filter_by(name=self.name).first()
            if not c:
                return True
        
        return False
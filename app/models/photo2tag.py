from .. import db

class Photo2Tag(db.Model):
    __tablename__ = 'photo2tag'
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'),
                        primary_key=True)

    tag_id = db.Column(db.Integer, db.ForeignKey('imgtags.id'),
                        primary_key=True)

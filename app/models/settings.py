from .. import db

class Settings(db.Model):
    __tablename__ = 'setting'
    id = db.Column(db.Integer, primary_key=True)
    # source_dir = db.Column(db.String(128), nullable=False)
    cpOrmv = db.Column(db.Boolean, nullable=False, default=False)
    splitfile = db.Column(db.Boolean, nullable=False, default=False)
    show = db.Column(db.Boolean, nullable=False, default=False)
    perview = db.Column(db.Boolean, nullable=False, default=False)


    def __repr__(self):
        return '<Tag %r>' % self.__tablename__


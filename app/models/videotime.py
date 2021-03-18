from .. import db
import datetime

class VideoTime(db.Model):
    __tablename__ = 'videotime'
    id = db.Column(db.Integer, primary_key=True)
    imgurl = db.Column(db.String(254))
    time = db.Column(db.Float)
    video_id = db.Column(db.Integer, db.ForeignKey('movies.id'))


    def __repr__(self):
        return '<Tag %r>' % self.time


    def changetime(self):
        return str(datetime.timedelta(seconds=float(self.time)))

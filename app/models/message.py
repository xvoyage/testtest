from .. import db
from flask import current_app
# from  ..lib.opfile import URL2physical, delfile,removevide, findPhysical, readfilePath


class MessageList(db.Model):
    __tablename__ = 'messageList'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64),nullable=False)
    path = db.Column(db.String(256),nullable=False)
    zt = db.Column(db.Boolean, default=True)
    task = db.Column(db.Integer, default=0)
    video_id = db.Column(db.Integer)
    file_id = db.Column(db.Integer)
    def __repr__(self):
        return '<Movie %r>' % self.name


    


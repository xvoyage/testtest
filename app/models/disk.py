from .. import db

class Diskdb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # DeviceID = db.Column(db.String(64), nullable=False)
    # SerialNumber = db.Column(db.String(64), nullable=False)
    DiskTotal = db.Column(db.Float, nullable=False)
    AliseName = db.Column(db.String(64), nullable=False)
    Path = db.Column(db.String(64), nullable=False)
    Status = db.Column(db.Boolean, nullable=False, default=False)
    uuid = db.Column(db.String(64))



    def __repr__(self):
        return '<Tag %r>' % self.DeviceID    
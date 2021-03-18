from .. import db
from .photo2tag import Photo2Tag
import collections
from ..lib.opfile import Removechar

class Myphoto(db.Model):
    __tablename__ = 'photo'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    imgurls = db.Column(db.Text)
    stats = db.Column(db.Integer)
    actorid = db.Column(db.Integer)
    tags = db.relationship('Photo2Tag',foreign_keys=[Photo2Tag.photo_id],
                            backref=db.backref('photos', lazy='joined'),
                            lazy='dynamic',
                            cascade='all, delete-orphan')

    def __repr__(self):
        return '<Myphoto %r>' % self.name

    @property
    def Imgs(self):
        if not self.imgurls:
            return ['../../static/upload/image/2/1.jpg']
        strurl = Removechar(self.imgurls)
        urlarr = strurl.split(';')
        # urldict = collections.OrderedDict()
        urllist = []
        for img in urlarr:
            urllist.append(img)
        return urllist

    @Imgs.setter
    def Imgs(self, value):
        self.imgurls = value

    def append_img(self, url):
        self.imgurls = self.imgurls + url

    def del_img(self, url):
        imgarr = self.Imgs
        for d in imgarr:
            if d == url:
                imgarr.remove(url)
        new_imgurls = ';'.join(imgarr)
        self.imgurls = new_imgurls+';'

    def remove_tag(self):
        tags = self.tags.all()
        if tags:
            for t in tags:
                db.session.delete(t)
            db.session.commit()

    def change_img(self, url):
        imgarr = self.Imgs
        for d in imgarr:
            if d == url:
                imgarr.remove(url)
        imgarr.insert(0,url)
        new_imgurls = ';'.join(imgarr)
        self.imgurls = new_imgurls+';'



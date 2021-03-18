from .. import db
import os
from datetime import datetime
from  ..lib.opfile import URL2physical, delfile,removevide, allowed_file, make_path, physical2URL, hash_file_name

class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    movies = db.relationship('Movie', backref='director',lazy='dynamic')

    @property
    def name2up(self):
        return self.name
    @name2up.setter
    def name2up(self,value):
        self.name = value
    
    def __repr__(self):
        return '<Director %r>' % self.name

class Producer(db.Model):
    __tablename__ = 'producer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    movies = db.relationship('Movie', backref='producer',lazy='dynamic')

    @property
    def name2up(self):
        return self.name
    @name2up.setter
    def name2up(self,value):
        self.name = value

    def __repr__(self):
        return '<producer %r>' % self.name

class Series(db.Model):
    __tablename__ = 'series'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    movies = db.relationship('Movie', backref='series',lazy='dynamic')

    @property
    def name2up(self):
        return self.name
    @name2up.setter
    def name2up(self,value):
        self.name = value

    def __repr__(self):
        return '<Series %r>' % self.name



class Zimu(db.Model):
    __tablename__ = 'zimu'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(512), nullable=False)
    name = db.Column(db.String(64),nullable=False)
    img = db.Column(db.String(128),nullable=False)
    status = db.Column(db.Boolean, default=True)
    zivalues = db.relationship('ZimuValue', backref='zimu',lazy='dynamic')
    hashpath = db.Column(db.String(256))
    skiptime = db.Column(db.Integer)

    @property
    def path(self):
        # name = os.path.basename(self.movie_file)
        # basename ='{0}_{1}'.format(self.id,self.name)
        # virpath = os.path.dirname(self.movie_file) + '/' + basename
        rootpath = 'D:\\code\mcms\\app'
        virpath = self.hashpath.replace('D:\\code\mcms\\app','')
        virpath = virpath.replace('\\','/')
        return virpath

    @path.setter
    def path(self, filepath):
        '''d
            filepath :文件名
        '''
        rootpath = 'D:\\code\mcms\\app\\static\\upload\\perview'
        datearry = datetime.now().utctimetuple()
        datepath ='{0}\\{1}\\{2}\\{3}\\'.format(rootpath, datearry[0],datearry[1],datearry[2])
        pypath = '{}{}'.format(datepath,filepath)
        # self.movie_file = '/video{0}'.format(self.pypath.replace('\\','/'))
        hashname = hash_file_name(pypath)
        self.hashpath = '{}{}'.format(datepath,hashname)

    def timeformat(self,vaule, fps=29.97):
        
        vaule = int(vaule) * float(1000/29.97)
        ms = int(vaule % 1000)
        print(ms)
        if ms < 10:
            ms = '00{}'.format(ms)
        elif ms < 100:
            ms = '0{}'.format(ms)
        vaule = vaule / 1000
        h = int(vaule / 3600);
        m = int((vaule % 3600) / 60)
        s = int((vaule % 60))
        
        return '{}:{}:{}.{}'.format(
            self.__formattime(h),
            self.__formattime(m),
            self.__formattime(s),
            ms
            )

    def checkfile(self,file):
        path = '{}\\{}.jpg'.format(self.hashpath, file)
        # print(self.hashpath)
        print(path,'dddd')

        if os.path.exists(path):
            return path
        return False

    def __formattime(self,t):
        if t < 10:
            return '0{}'.format(t)
        return str(t)

    def __repr__(self):
        return '<Zimu %r>' % self.name


class ZimuValue(db.Model):
    __tablename__ = 'zimuvalue'
    id = db.Column(db.Integer, primary_key=True)
    starttime = db.Column(db.String(64), nullable=False)
    endtime = db.Column(db.String(64), nullable=False)
    zmvalue = db.Column(db.String(512), nullable=False)
    pid = db.Column(db.Integer, db.ForeignKey('zimu.id'))
    xuhao = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<ZimuValue %r>' % self.zmvalue

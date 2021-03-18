from .. import db, disklist, qe
# from .actor import Actor
from .tag import Tag
from .actor import Actor
# from .category import Category
from  ..lib.opfile import URL2physical, delfile,removevide, allowed_file, make_path, physical2URL, hash_file_name
from .movie2actor import Movie2Actor
from .movie2tag import Movie2Tag
import os
import configparser
from datetime import datetime
import shutil
import cv2
import numpy


# registrations = db.Table('movie2actor',
#                     db.Column('actor_id', db.Integer, db.ForeignKey('actors.id')),
#                     db.Column('movie_id', db.Integer, db.ForeignKey('movies.id'))
#                     )

# movie2tag_registrations = db.Table('movie2tag',
#                     db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')),
#                     db.Column('movie_id', db.Integer, db.ForeignKey('movies.id'))
#                     )

# class Movie2Tag(db.Model):
#     __tablename__ = 'movie2tag'
#     tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'),
#                         primary_key=True)
#     movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'),
#                         primary_key=True)


# class Movie2Actor(db.Model):
#     __tablename__ = 'movie2actor'
#     actor_id = db.Column(db.Integer, db.ForeignKey('actors.id'),
#                         primary_key=True)
#     movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'),
#                         primary_key=True)    




class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(512), nullable=False)

    cate_id = db.Column(db.Integer, db.ForeignKey('categorys.id'))
    director_id = db.Column(db.Integer, db.ForeignKey('director.id'))
    producer_id = db.Column(db.Integer, db.ForeignKey('producer.id'))
    series_id = db.Column(db.Integer, db.ForeignKey('series.id'))
    name = db.Column(db.String(64),nullable=False)
    img = db.Column(db.String(128),nullable=False)

    stats = db.Column(db.Integer, default=0)
    movie_file = db.Column(db.String(128))
    description = db.Column(db.Text)
    video_times = db.relationship('VideoTime', backref='video')
    ares = db.Column(db.Integer, default=0)
    splitfile = db.Column(db.Boolean, default=True)
    pypath = db.Column(db.String(256))
    hashpath = db.Column(db.String(256))
    # filesize = db.Column(db.BigInteger)
    size = db.Column(db.BigInteger)
    diskpart = db.Column(db.String(64))
    sceen = db.Column(db.String(64))
    ex_name = db.Column(db.String(64))
    uuid = db.Column(db.String(64))
    chinese = db.Column(db.Boolean, default=False)
    date = db.Column(db.Date)
    _durtime = db.Column(db.Integer)
    perview = db.Column(db.Boolean,default=False)
    ismove = db.Column(db.Boolean,default=False)

    video_files = db.relationship('VideoFile', backref='video',lazy='dynamic')

    # actors = db.relationship('Actor', 
    #                             secondary=registrations,
    #                             backref=db.backref('movies', lazy='dynamic'),
    #                             lazy='dynamic')

    # tags = db.relationship('Tag', 
    #                             secondary=movie2tag_registrations,
    #                             backref=db.backref('movies', lazy='dynamic'),
    #                             lazy='dynamic')

    tag = db.relationship('Movie2Tag',foreign_keys=[Movie2Tag.movie_id],
                            backref=db.backref('movies', lazy='joined'),
                            lazy='dynamic',
                            cascade='all, delete-orphan')
    actor = db.relationship('Movie2Actor',foreign_keys=[Movie2Actor.movie_id],
                            backref=db.backref('movies', lazy='joined'),
                            lazy='dynamic',
                            cascade='all, delete-orphan')
    def __repr__(self):
        return '<Movie %r>' % self.title

    @property
    def durtime(self):
        if self._durtime:
            h = int(self._durtime / 3600);
            m = int((self._durtime % 3600) / 60)
            s = int((self._durtime % 60))
            return '{}:{}:{}'.format(h,m,s)
        return 'N/A'
    
    @durtime.setter
    def durtime(self,value):
        self._durtime = value


    @property
    def name2up(self):
        return self.name;
    
    @name2up.setter
    def name2up(self, name):
        self.name = name.upper()

    @property
    def path(self):
        name = os.path.basename(self.movie_file)
        basename ='{0}_{1}'.format(self.id,name)
        virpath = os.path.dirname(self.movie_file) + '/' + basename
        return virpath

    @path.setter
    def path(self, filepath):
        '''
            filepath :文件名
        '''
        datearry = datetime.now().utctimetuple()
        datepath ='\\{0}\\{1}\\{2}\\'.format(datearry[0],datearry[1],datearry[2])
        self.pypath = '{}{}'.format(datepath,filepath)
        self.movie_file = '/video{0}'.format(self.pypath.replace('\\','/'))
        hashname = hash_file_name(self.pypath)
        self.hashpath = '{}{}\\{}'.format(datepath,hashname,hashname)
        self.diskpart = self.pypath.split('\\')[0] + '\\'





    def remove_actor(self):
        actors = self.actor.filter_by(movie_id=self.id).all()
        if actors :
            # db.session.delete(f)
            for a in actors:
                db.session.delete(a)
            db.session.commit()

    def readActors(self):
        return db.session.query(Actor).select_from(Movie2Actor).filter_by(movie_id=self.id).join(Actor, Movie2Actor.actor_id==Actor.id)

    def readTags(self):
        return db.session.query(Tag).select_from(Movie2Tag).filter_by(movie_id=self.id).join(
                        Tag, Movie2Tag.tag_id==Tag.id)

    def remove_tag(self):
        tags = self.tag.filter_by(movie_id=self.id).all()
        if tags:
            for t in tags:
                db.session.delete(t)
            db.session.commit()

    def remove_imgandvideo(self, disks):
        imgpath = URL2physical(self.img)
        if imgpath != r'D:\code\mcms\app\static\upload\image\zd.jpg':
            delfile(imgpath)



    def check_name(self):
        if self.name is not None:
            c = Movie.query.filter_by(name=self.name).first()
            # if not c or (c.id == self.id):
            #     return True
            if not c:
                return True
        
        return False


    def isonline(self):
        disk = disklist.get(self.uuid,None)
        if disk is not None:
            pypath = '{}{}'.format(disk, self.pypath)
            hashpath = '{}{}'.format(disk,self.hashpath)
            vd = self.video_files.first()
            if vd:
                file = '{}{}'.format(disk, vd.pyurl)
                if file:
                    return True
        return False

    def findfile(self,disklist):
        disk = disklist.get(self.uuid, None)
        if disk is not None:
            pypath ='{}{}'.format(disk,self.pypath)
            if os.path.exists(pypath):
                return True;
        return  False

    def get_file_message(self,disklist):
        mesg = {}
        disk = disklist.get(self.uuid,None)
        if disk is not None:
            pypath = '{}{}'.format(disk, self.pypath)
            hashpath = '{}{}'.format(disk,self.hashpath)

            if os.path.exists(pypath):
                path = pypath
            if os.path.exists(hashpath):
                path = hashpath
            mesg['size'] = '%.2f' % (self.size / (1024*1024*1024))
            mesg['path'] = path
        else:
            mesg['path'] = u'文件处于离线中'
            mesg['size'] = '%.2f' % (self.size / (1024*1024*1024))
        return mesg

    def ishd(self):
        if self.video_files:
            hd = self.video_files.first()
            if hd:
                if hd.height:
                    return hd.height
        return False




class VideoFile(db.Model):
    __tablename__ = 'videlfile'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64),nullable=False)
    hashname = db.Column(db.String(256))
    physical_path = db.Column(db.String(256), nullable=False)
    part_uuid = db.Column(db.String(64), nullable=False)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    crame_count = db.Column(db.Integer)
    fps = db.Column(db.Integer)
    prew = db.Column(db.Boolean,default=False)
    parting = db.Column(db.Boolean,default=False)
    ismove = db.Column(db.Boolean,default=False)
    __durtime = db.Column(db.Integer)
    size = db.Column(db.BigInteger)
    video_id = db.Column(db.Integer, db.ForeignKey('movies.id'))

    @property
    def fileid(self):
        return '{}_{}'.format(self.video_id, self.id)
    @fileid.setter
    def fileid(self, value):
        raise ValueError(u'fileid属性不支持赋值')
    @property
    def videosize(self):
        if self.size:
            return '%.2f G' % (float(self.size) / (1024*1024*1024))
        else:
            return 'N/A'
    @videosize.setter
    def videosize(self, value):
        raise ValueError(u'videosize属性不支持赋值')


    @property
    def pyurl(self):
        if self.parting:
            return '{}\\{}'.format(self.physical_path, self.hashname)
        else:
            return '{}\\{}'.format(self.physical_path, self.name)

    @pyurl.setter
    def pyurl(self, value):
        raise ValueError(u'pyurl属性不能赋值')
    @property
    def video_url(self):
        return '/video/{}'.format(self.id)

    @video_url.setter
    def video_url(self, value):
        raise ValueError(u'不可以赋值')

    @property
    def durtime(self):
        if self.__durtime:
            h = int(self.__durtime / 3600);
            m = int((self.__durtime % 3600) / 60)
            s = int((self.__durtime % 60))
            return '{}:{}:{}'.format(h,m,s)
        return 'N/A'
    
    @durtime.setter
    def durtime(self,value):
        self.__durtime = value



    #-----------------分割视频------------------------------
    def splitfile(self,videopath,hashfile,size=1024*1024*100):
        '''
        videopath: 源文件路径
        '''
        if not self.video_id or self.video_id is None:
            raise 'err'
        mid = self.video_id
        nfname = os.path.basename(hashfile)
        newdir = os.path.dirname(hashfile)
        filesize = os.path.getsize(videopath)
        qe.put([mid,0,2])
        total = int(filesize)
        findex = 0 
        with open(videopath,'rb') as fr:
            while fr.tell() < total:
                try:
                    fr.seek(fr.tell())
                    file_pd = fr.read(size)
                    nfile = nfname + str(findex)
                    desfile = os.path.join(newdir, nfile)
                    nf = open(desfile, 'wb')
                    nf.write(file_pd)
                    nf.close()
                    findex += 1
                    pers = float(findex*size) / total
                    pers = float('%.2f' % pers)
                    if pers > 1:
                        pers = 1
                    qe.put([mid,pers,-1])
                    print('分割进度:{}%'.format(pers))
                except IOError as e:
                    break
        qe.put([mid,100,3])

    #还原文件(文件片合并)
    def nrsfile(self, pypath, hashpath,status=True):
        if not self.video_id or self.video_id is None:
            raise 'err'
        if not os.path.exists(hashpath):
            raise ValueError(u'配置文件不存在')
        vid = self.video_id
        config = configparser.ConfigParser()
        config.read(hashpath)
        tatal = float(config['Default']['size'])
        dbsize = float(config['Default']['dpsize'])
        fname = os.path.basename(pypath)
        chumk = 0
        with open(pypath, 'wb') as fr:
            while True:
                try:
                    pdfile = hashpath + '{0}'.format(chumk)
                    source_file = open(pdfile,'rb')
                    fr.write(source_file.read())
                    source_file.close()
                    if status:
                        os.remove(pdfile)
                except IOError as e:
                    break
                chumk += 1
                pers = float(chumk*dbsize) / tatal
                pers = float('%.2f' % pers)
                if pers > 1:
                    pers = 1
                qe.put([vid, pers])
        qe.put([-1,'{0}整合完成'.format(pypath)])
    

    # 生成缩略图
    def resize_image(self,image, height=102, width=180):
        top, bottom, left, right= (0,0,0,0)
        h, w, o = image.shape
        longest_edge = max(h,w)
        black = [0,0,0]
        constant = cv2.copyMakeBorder(image,top,bottom,left,right, cv2.BORDER_CONSTANT, value=black)
        return cv2.resize(constant,(width, height))

    def save_img(self,image,addr,num):
        path = os.path.join(addr,'{}.jpg'.format(num))
        rsimg = resize_image(image)
        cv2.imwrite(path,rsimg,[cv2.IMWRITE_JPEG_QUALITY,100])


    def create_zo_img(self,width=180, height=102):
        I=numpy.zeros((5*height,width*10),dtype=numpy.uint8)
        I=cv2.cvtColor(I,cv2.COLOR_GRAY2BGR)
        return I

    def write_into_img(self,dicimg, srcimg, top,left,width, height):
        dicimg[top:top+height,left:left+width] = srcimg[0:height,0:width]
        return dicimg

    def init_video_img(self,video,imgpath, jg=1):
        if not self.video_id or self.video_id is None:
            raise 'err'
        vid = self.id
        dname = os.path.dirname(imgpath)
        if not os.path.exists(dname):
            os.makedirs(dname)
        # qe.put([vid,0,0])
        cap = cv2.VideoCapture(video)
        fps = round(cap.get(5) * jg)
        virpath = '/img/{}_' + os.path.basename(imgpath) +'{}'
        fpscount = int(cap.get(7))
        jilu =[]
        i = 0
        j = 0
        img = None
        rows = 0
        coloums = 0
        success ,frame = cap.read()
        while success:
            i += 1
            if (i % fps ==0):
                if coloums >= 10:
                    rows +=1
                    coloums = 0
                    if rows >= 5:
                        filename = imgpath + str(j) + '.jpg'
                        cv2.imwrite(filename,img)
                        persent = float((50*fps*(j+1))/fpscount)
                        persent = float('%.2f' % persent)
                        print('总帧数：', fpscount)
                        print('以读帧数:',(50*fps*(j+1)))
                        print(persent)
                        qe.put([vid,persent,-1])
                        rows = 0
                        j += 1
                        img = None
                if img is None:
                    img = self.create_zo_img()
                rsimg = self.resize_image(frame)
                self.write_into_img(img,rsimg,rows*102,coloums*180,180,102)
                line = '{0}.jpg#xywh={1},{2},180,102'.format(virpath.format(vid,j),coloums*180,rows*102)
                jilu.append(line)
                coloums += 1
            success, frame = cap.read()
        
        if img is not None:
            filename = imgpath + str(j) + '.jpg'
            cv2.imwrite(filename,img)
        qe.put([vid,100,1])
        return jilu

#-----------------生成缩略图结束----------------------
    #获取配置文件目录
    def  get_config_dir(self):
        if self.ismove:
            return self.physical_path
        else:
            if self.parting:
                part = self.physical_path
            else:
                part = '{}\\{}'.format(self.physical_path,self.hashname)
            return part
    #获取预览图目录
    def get_perview_dir(self):
        if self.ismove:
            return '{}\\{}'.format(self.physical_path, 'view')
        else:
            if self.parting:
                return '{}\\{}'.format(self.physical_path, 'view')
            else:
                return '{}\\{}\\{}'.format(self.physical_path, self.hashname, 'view')
from .. import db
from flask_wtf import FlaskForm
from ..models import Movie, Category, Producer, Director, Series, Movie2Tag, Movie2Actor, Tag, Actor
from ..lib.javlib import checkimgurl
class VideoController(object):


    #movies对象数据绑定
    def video_bind_data(self, formdata, vid=None):
        # pass
        if not isinstance(formdata, FlaskForm):
            raise ValueError(u'数据类型错误')
        video_id = Movie.query.filter_by(name=formdata.name.data).first()
        if video_id:
            if not video_id.id == vid:
                raise ValueError(u'视频已存在库中')
        cy = self.add_simple(Category, False, formdata.name.data.split('-')[0])
        if not cy:
            raise ValueError(u'视频类别生成失败')

        pr = self.add_simple(Producer,formdata.producer.data,formdata.producer_text.data)
        if not pr:
            raise ValueError(u'视频导演属性生成失败')
        dr = self.add_simple(Director,formdata.director.data,formdata.director_text.data)
        if not dr:
            raise ValueError(u'视频厂商属性生成失败')
        sr = self.add_simple(Series,formdata.series.data,formdata.series_text.data)
        if not sr:
            raise ValueError(u'视频系列属性生成失败')

        if vid is None:
            video = Movie()
        else:
            video = Movie.query.get_or_404(vid)
            if formdata.imgurl.data != video.img:
                video.remove_imgandvideo('d')
        video.title = formdata.title.data
        video.name2up = formdata.name.data.strip()
        video.img = checkimgurl(formdata.imgurl.data)
        video.stats = formdata.stats.data[0]
        video.description = formdata.des.data
        video.ares = formdata.ares.data[0]
        video.category = cy
        video.producer = pr
        video.director = dr
        video.series = sr
        video.splitfile = formdata.splitfile.data
        video.ex_name = formdata.bsname.data.split('.')[-1]
        video.date = formdata.date.data
        video.chinese = formdata.ischinese.data
        video.perview = formdata.isperview.data
        video.ismove = formdata.ismove.data

        tag_md_list =self.add_multiple(Tag,formdata.tid.data,formdata.tid_text.data)
        if tag_md_list:
            for tag_md in tag_md_list:
                mt = Movie2Tag(tags=tag_md, movies=video)
                db.session.add(mt)

        actor_md_list = self.add_multiple(Actor,formdata.aid.data,formdata.aid_text.data)
        if actor_md_list:
            for actor_md in actor_md_list:
                ma = Movie2Actor(actors=actor_md, movies=video)
                db.session.add(ma)

        return video


    
    #form对象数据绑定
    def form_bind_data(self,videoobj, formobj):
        if not isinstance(formobj, FlaskForm):
            raise ValueError(u'类型错误')
        if not isinstance(videoobj, Movie):
            raise ValueError(u'数据类型错误')
        formobj.title.data = videoobj.title
        formobj.name.data = videoobj.name2up
        formobj.imgurl.data = videoobj.img
        formobj.stats.data = [str(videoobj.stats)]
        formobj.des.data = videoobj.description
        # formobj.movieurl.data = videoobj.movie_file
        # form.bsname.data = os.path.basename(video.movie_file)
        # formobj.cid.data = [str(videoobj.category.id)]
        formobj.ares.data = [str(videoobj.ares)]
        formobj.aid.data = [str(x.actor_id) for x in videoobj.actor.all()]
        formobj.tid.data = [str(x.tag_id) for x in videoobj.tag.all()]
        formobj.splitfile.data = videoobj.splitfile
        formobj.date.data = videoobj.date
        formobj.ischinese.data = videoobj.chinese
        formobj.isperview.data = videoobj.perview
        formobj.producer.data = [str(videoobj.producer_id)]
        formobj.director.data = [str(videoobj.director_id)]
        formobj.series.data = [str(videoobj.series_id)]
        

    #显示video列表
    def show_video_list(self):
        pass
    
    #删除所有标签
    def del_all_tag(self, video):
        for t in video.tag:
                tid = video.tag.filter_by(movie_id=video.id).first()
                if tid:
                    db.session.delete(tid)

    #删除所有所有演员
    def del_all_actors(self, video):
        for a in video.actor:
                vid = video.actor.filter_by(movie_id=video.id).first()
                if vid:
                    db.session.delete(vid)
        

    #显示video详情
    def show_video_details(self,videoid_fileid):
        #获取视频对象


        #获取视频的所有标签
        # tags = db.session.query(Tag).select_from(Movie2Tag).filter_by(movie_id=video.id).join(Tag, Movie2Tag.tag_id==Tag.id)
        #获取视频的所有演员

        #获取视频文件信息
        # video_file 
        #获取预览图片信息
        pass

    
    def add_simple(self,modelclass,selectdata,inputdata):
        cy = False
        if selectdata:
            if isinstance(selectdata,list):
                selectdata = selectdata[0]
            cy = modelclass.query.filter_by(id=int(selectdata)).first()
        
        if inputdata:
            cid_text = inputdata.upper()
            c_cate = modelclass.query.filter_by(name=cid_text).first()
            if c_cate:
                cy = c_cate
            else:
                cli = modelclass(

                    name2up = cid_text

                )
                db.session.add(cli)
                cy = cli

        return cy

    def add_multiple(self,modelclass,selectdata,texts):
        modellist = []
        if texts:
            aid_text_strip = texts.strip(';')
            aid_arr = aid_text_strip.split(';')
            for aid_name  in aid_arr:
                a_obj = modelclass.query.filter_by(name=aid_name).first()
                if a_obj:
                    for obj_id in selectdata:
                        if a_obj.id == int(obj_id):
                            break
                    else:
                        modellist.append(a_obj)

                else:
                    act = modelclass(
                        name = aid_name,
                        sortnum = 99
                    )
                    db.session.add(act)
                    modellist.append(act)

        for actor in selectdata:
                a = modelclass.query.filter_by(id = int(actor)).first()
                if a:

                    modellist.append(a)
        return modellist
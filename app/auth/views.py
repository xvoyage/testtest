from flask import render_template, redirect, request, url_for, flash, current_app, send_from_directory, jsonify, Response, session, get_flashed_messages, g, abort
from . import auth
from .forms import LoginForm, MovieForm, CategoryForm, TagForm, ActorForm, DiskForm, SettingForm, ZimuForm
from ..models import User, Category, Tag, Actor, Movie, Movie2Actor, Movie2Tag, Diskdb, Settings, MessageList, Myphoto, Producer, Director, Series, ZimuValue, Zimu,VideoFile
from flask_login import login_user, current_user, login_required, logout_user
from flask_uploads import UploadSet, IMAGES, All, configure_uploads, patch_request_class
import os
from .. import  db, socketio, qe,disklist
from ..lib.opfile import upload_file,delfile, allowed_file, make_path, check_dir_file, physical2URL, searchfile, movefile,  removevide, get_fs_info, get_COPY_FILE_DES, restorefile,  get_sesion_value, clean_sesion_value, set_sesion_value, restoretask, hash_file_name, get_UPLOADED_FILES_DEST, upload_base64,perview_restorefile,get_video_msg, aysc_init_zimu_img
from flask_ckeditor import upload_fail, upload_success
import re
import time
import datetime
import configparser
from  sqlalchemy.sql.expression import or_, func, and_
from urllib import parse
from ..lib.searchvideo import getvideomsg, checkimgurl
# from ..lib.messagequeue import MessageQueue
from flask_socketio import emit
from threading import Lock
from ..lib.diskdrive import Diskdrive
from ..lib.javlib import make_request, get_video_meg,checkimgurl, javlib_search_video_msg
from ..lib.javdb import  JavDbModeController
from ..lib.javbus import JavBusModeController
from pypinyin import lazy_pinyin
from collections import OrderedDict
import json
from ..lib.langconv import *
from ..lib.op_video import add_simple,add_multiple
from ..lib.es_videos import Esvideos
import shutil
from ..controller import VideoFileController,VideoController,Diskcontroller, SettingController



thread = None
thread_lock = Lock()

def check_queue(app):
    with app.app_context():
        while True:
            
            socketio.sleep(3)
            if qe.qsize():
                mglists = []
                while qe.qsize():
                    mg = qe.get()
                    mglists.append(mg)
                socketio.emit('server_response',{'data': mglists}, namespace='/messagequeue')

            # mglists = [[-1,'???????????????']]
            # socketio.emit('server_response',{'data': mglists}, namespace='/messagequeue')
                



@socketio.on('connect', namespace='/messagequeue')
def connect():
    global thread
    with thread_lock:
        if thread is None:
            app = current_app._get_current_object()
            thread = socketio.start_background_task(check_queue, app)

        




@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            get_flashed_messages() #????????????
            flash('????????????','success')
            # vd = VdFollow()
            # app = current_app._get_current_object()
            # vd.async_check_video(app)
            return redirect(request.args.get('next') or url_for('auth.list_video', username=current_user.username, stats=4))
    return render_template('auth/login.html', form=form)


@auth.route('/logout', methods=['POST','GET'])
@login_required
def logout():
    logout_user()
    # flash('You have been logged out.')
    return redirect(url_for('auth.login'))




#-------????????????---------
# ????????????
@auth.route('/add', methods=['GET', 'POST'])
@login_required
def Add():
    form = CategoryForm()
    form.ddlParentId.choices.insert(0, ('0', u'???????????????'))
    if form.validate_on_submit():
        cli = Category(
            pid = form.ddlParentId.data,
            name2up = form.txtTitle.data,
            sortnum = form.txtSortId.data,
            description = form.txtDescription.data
        )
        if not cli.check_name():
            flash('???????????????','err')
            return redirect(url_for('auth.Add'))
        db.session.add(cli)
        db.session.commit()
        return redirect(url_for('auth.category_list'))
    return render_template('auth/classification_add.html',form=form)
    # return render_template('auth/index.html',form=form)


# flask_ckeditor????????????
@auth.route('/upload', methods=[ 'POST'])
def file_upload():
    # files = request.files.getlist('moviefile[]')
    # for file in files:
    #     file.save(os.path.join(r'F:\code\mcms\app\static',file.filename))
    f = request.files.get('upload')
    try:
        url = upload_file(f)
        return upload_success(url=url)
    except Exception as e:
        # return upload_fail(str(e))
        raise str(e)


@auth.route('/clist', methods=['GET','POST'])
@login_required
def category_list():
    ed = session.get('cg',False)
    cgs = Category.query.all()
    cgsdict = OrderedDict()
    for cg in cgs:
        piny = cg.name[0].lower()
        zm = cgsdict.get(piny,None)
        if zm is None:
            cgsdict[piny] = [cg]
        else:
            zm.append(cg)
    ordercg = OrderedDict(sorted(cgsdict.items(),key=lambda t: t[0]))

    return render_template('auth/classification_list.html', 
            cgs = ordercg,
            ed = ed
        )
@auth.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    category = Category.query.get_or_404(id)
    form = CategoryForm()
    form.ddlParentId.choices.insert(0, ('0', u'???????????????'))
    if form.validate_on_submit():
        
        category.pid = form.ddlParentId.data
        category.name2up = form.txtTitle.data
        category.sortnum = form.txtSortId.data
        category.description = form.txtDescription.data
        try:
            db.session.add(category)
            db.session.commit()
            return redirect(url_for('auth.category_list'))
        except Exception as e:
            flash('??????????????????????????????????????????','err')
            return redirect(url_for('auth.edit_category', id = id))
    form.ddlParentId.data = category.pid
    form.txtTitle.data = category.name2up
    form.txtDescription.data = category.description
    form.txtSortId.data = category.sortnum
    return render_template('auth/classification_add.html', form=form)

@auth.route('/c_delete', methods=['GET','POST'])
@login_required
def category_delete():
    if request.method == 'GET':
        tid = request.args.get('id')
        arr = [tid,]
    if request.method == 'POST':
        arr = request.values.getlist('checked_arry')
    if arr:
        for cid in arr:
            category = Category.query.filter_by(id=int(cid)).first()
            db.session.delete(category)
        db.session.commit()
    return redirect(url_for('auth.category_list'))

@auth.route('/cg_st', methods=['GET'])
@login_required
def cg_st():
    stus = request.args.get('status')
    if stus:
        if stus == 'edit':
            session['cg'] = True
        else:
            session['cg'] = False
    return redirect(url_for('auth.category_list'))

#---------????????????end-----------

#----------????????????----------------


#????????????
@auth.route('/tag_add', methods=['GET', 'POST'])
@login_required
def Tag_Add():
    form = TagForm()
    if form.validate_on_submit():
        cli = Tag(
            name = form.txtTitle.data,
            sortnum = form.txtSortId.data,
            
        )
        if not cli.check_name():
            flash('???????????????','err')
            return redirect(url_for('auth.Tag_Add'))
        db.session.add(cli)
        db.session.commit()
        return redirect(url_for('auth.Tag_list'))
    return render_template('auth/tag_add.html',form=form)


@auth.route('/tags_st', methods=['GET'])
@login_required
def tags_st():
    stus = request.args.get('status')
    if stus:
        if stus == 'edit':
            session['status'] = True
        else:
            session['status'] = False
    return redirect(url_for('auth.Tag_list'))


@auth.route('/tlist', methods=['GET','POST'])
@login_required
def Tag_list():
    ed = session.get('status',False)
    # ed = False
    tags = Tag.query.all()
    tagsdict = OrderedDict()
    for tag in tags:
        piny = lazy_pinyin(tag.name)[0][0].lower()
        zm = tagsdict.get(piny,None)
        if zm is None:
            tagsdict[piny] = [tag]
        else:
            zm.append(tag)
    ordertag = OrderedDict(sorted(tagsdict.items(),key=lambda t: t[0]))

    return render_template('auth/tag_list.html', 
            tags = ordertag,
            ed = ed
        )


#------????????????-----
@auth.route('/tag_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_tag(id):
    tag = Tag.query.get_or_404(id)
    form = TagForm()
    if form.validate_on_submit():
        tag.name = form.txtTitle.data
        tag.sortnum = form.txtSortId.data
        try:
            db.session.add(tag)
            db.session.commit()
            return redirect(url_for('auth.Tag_list'))
        except Exception as e:
            flash('???????????????????????????????????????','err')
            return redirect(url_for('auth.edit_tag', id=id))
    form.txtTitle.data = tag.name
    form.txtSortId.data = tag.sortnum
    return render_template('auth/tag_add.html', form=form)

 #----????????????-----

@auth.route('/t_delete', methods=['GET','POST'])
@login_required
def tag_delete():
    if request.method == 'GET':
        tid = request.args.get('id')
        arr = [tid,]
    if request.method == 'POST':
        arr = request.values.getlist('checked_arry')
    if arr:
        for cid in arr:
            tag = Tag.query.filter_by(id=int(cid)).first()
            db.session.delete(tag)
        db.session.commit()
    return redirect(url_for('auth.Tag_list'))


#---renwu??????
@auth.route('/actor_add', methods=['GET', 'POST'])
@login_required
def add_arctor():

    form = ActorForm()
    if form.validate_on_submit():
        cli = Actor(
            name = form.txtTitle.data,
            sortnum = form.txtSortId.data,
            description = form.txtDescription.data
        )
        imgs_base64 = form.imgurl.data
        if imgs_base64:
            imgurl = upload_base64(imgs_base64)
            cli.imgurl = imgurl
        if not cli.check_name():
            flash('???????????????','err')
            return redirect(url_for('auth.add_arctor'))
        db.session.add(cli)
        db.session.commit()
        
        return redirect(url_for('auth.list_actor'))
    return render_template('auth/actor_add.html',form=form)


@auth.route('/alist', methods=['GET','POST'])
@login_required
def list_actor():
    page = request.args.get('page', 1, type = int)
    actors = [(str(x.id), x.name) for x in Actor.query.all()]
    
    querystr = Actor.query
    name = request.form.get('act')
    if name:
        querystr = Actor.query.filter_by(id = int(name))
    # per_page = current_app.config['CATEGORY_PER_PAGE']
    pagination = querystr.order_by(Actor.love.desc()).paginate(
        page, per_page = 14,
        error_out = False
    )
    taglist = pagination.items
    return render_template('auth/actor_list.html', 
            taglist = taglist,
            pagination = pagination,
            actors = actors
        )


@auth.route('/actor_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_actor(id):
    if request.method == 'GET':
        if request.referrer and request.referrer != request.url:
            session['pre'] = request.referrer
    actor = Actor.query.get_or_404(id)
    form = ActorForm()
    if form.validate_on_submit():
        preurl = session.get('pre',url_for('auth.list_video'))
        actor.name = form.txtTitle.data
        actor.sortnum = form.txtSortId.data
        actor.description = form.txtDescription.data
        imgs_base64 = form.imgurl.data
        if imgs_base64:
            if imgs_base64.startswith('data:image'):
                imgs_base64 = upload_base64(imgs_base64)
            actor.imgurl = imgs_base64
        try:
            db.session.add(actor)
            db.session.commit()
            return redirect(preurl)
        except Exception as e:
            flash('????????????,????????????????????????','err')
            return redirect(url_for('auth.edit_actor'), id=id)
    form.txtTitle.data = actor.name
    form.txtSortId.data = actor.sortnum
    form.txtDescription.data = actor.description
    form.imgurl.data = actor.imgurl
    return render_template('auth/actor_add.html', form=form)

@auth.route('/actor_like',methods=['GET','POST'])
@login_required
def actor_like():
    cig = request.args.get('id')
    if not cig:
        raise 'err'
    cg = Actor.query.get_or_404(cig)
    if cg.love:
        cg.love = False
    else:
        cg.love = True
    db.session.add(cg)
    db.session.commit()
    return jsonify({'status':cg.love})


@auth.route('/a_delete', methods=['GET','POST'])
@login_required
def delete_actor():
    if request.method == 'GET':
        tid = request.args.get('id')
        arr = [tid,]
    if request.method == 'POST':
        arr = request.values.getlist('checked_arry')
    if arr:
        for cid in arr:
            actor = Actor.query.filter_by(id=int(cid)).first()
            db.session.delete(actor)
        db.session.commit()
    return redirect(url_for('auth.list_actor'))



#---------------------??????------------------------

@auth.route('/iupload', methods=[ 'POST','GET'])
def m_upload():
    # return jsonify({'uploadfile':'url'})
    f = request.files.get('upload')
    try:
        url = upload_file(f)
        return jsonify({'uploadfile':url})
    except Exception as e:
        # return upload_fail(str(e))
        raise str(e)


@auth.route('/idelete', methods=['POST'])
@login_required
def im_delete():
    file = request.form.get('imgorfile')
    file = file.replace('/video','')
    if delfile(file):
        return jsonify({'result':'ok'})
    else:
        raise 'err'

#------------------??????------------------------
@auth.route('/video_add', methods=['GET', 'POST'])
@login_required
def add_video():
    sett = SettingController().get_settings()
    form = MovieForm(
        stats=['0'],
        ares=['0'],
        splitfile = sett.splitfile,
        isperview = sett.perview,
        ismove = sett.cpOrmv
    )

    if form.validate_on_submit():
        try:
            video_controller = VideoController()
            #??????????????????
            video = video_controller.video_bind_data(form)
            videofile_controller = VideoFileController(disklist)
            #????????????????????????
            video_file = videofile_controller.add_video_file(video,form.movieurl.data)
            video_file.video= video
            video.uuid = video_file.part_uuid
            db.session.add(video)
            db.session.add(video_file)
            db.session.commit()
            db.session.refresh(video_file)
            db.session.expunge(video_file)

            st = videofile_controller.check_message(video_file)
            if st:
                raise ValueError(u'??????????????????????????????????????????')

            appcontext = current_app._get_current_object()
            #??????????????????
            videofile_controller.async_option_video_file(appcontext,video_file, form.movieurl.data)
            flash(form.name.data+'???????????????????????????','success')
            return redirect(url_for('auth.list_video'))
        except Exception as e:
            raise(e)
            flash(str(e),'err')
            db.session.rollback()
            return redirect(url_for('auth.add_video'))

    return render_template('auth/movie_add.html', form=form, filelist=[])
    




@auth.route('/video_list', methods=['GET', 'POST'])
@login_required
def list_video():
    page = request.args.get('page', 1, type = int)
    searchtag = request.args.get('tag')
    searchactor = request.args.get('actor')
    searchcate = request.args.get('cate')
    statslist = request.args.get('stats')
    areslist = request.args.get('ares')
    videname = request.args.get('fh')
    searchuuid = request.args.get('uuid')

    tj = set()
    sett = SettingController().get_settings()
    if sett.show:
        for uuid in disklist.keys():
            tj.add(Movie.uuid == uuid)

    videoquery = Movie.query.filter(or_(*tj))
    # es = Esvideos([{'host':'127.0.0.1','port':9200}],3600)
    # es.allstr()

    if searchuuid:
        videoquery = Movie.query.filter_by(uuid=searchuuid)

    if searchtag:

        videoquery = db.session.query(Movie).select_from(Movie2Tag).filter(and_(or_(*tj), Movie2Tag.tag_id == int(searchtag))).join(
                        Movie, Movie2Tag.movie_id==Movie.id)

    if searchactor:

        videoquery = db.session.query(Movie).select_from(Movie2Actor).filter(and_(or_(*tj)), Movie2Actor.actor_id == int(searchactor)).join(
                        Movie, Movie2Actor.movie_id==Movie.id)

    if searchcate:

        videoquery = Movie.query.filter(and_(or_(*tj)), Movie.cate_id == int(searchcate))

    if statslist:

        videoquery = Movie.query.filter(and_(or_(*tj)), Movie.stats >= int(statslist)).order_by(Movie.stats.desc())


    if areslist:
      
        videoquery = Movie.query.filter(and_(or_(*tj)), Movie.ares == int(areslist))

    if videname:

        videoquery = Movie.query.filter(and_(or_(*tj)), Movie.name.like('%'+ videname + '%')).order_by(Movie.name.desc())
        tag = Tag.query.filter_by(name=videname).first()
        if tag:
            videoquery = db.session.query(Movie).select_from(Movie2Tag).filter(and_(or_(*tj), Movie2Tag.tag_id == int(tag.id))).join(
                            Movie, Movie2Tag.movie_id==Movie.id)

    st = time.time() * 1000
    pagination = videoquery.order_by(Movie.id.desc()).paginate(
        page, per_page = current_app.config['CATEGORY_PER_PAGE'],
        error_out = False
    )
    tags = Tag.query.all()
    cateids = Category.query.all()
    movielist = pagination.items
    ml = MessageList.query.all()
    # for m in ml:
    #     for movie in movielist:
    #         if m.video_id == movie.id:
    #             movie.task = True
    #         else:
    #             movie.task = False
    
    # es.nestedstr('tags','?????????')
    
    # movielist = es.start_search(page)
    # pagination = es.pagination

    rti = time.time() * 1000 - st
    return render_template('auth/movie_list.html', 
            # movielist = movielist
            movielist = movielist,
            pagination = pagination,
            tagid = searchtag,
            actorid = searchactor,
            cid = searchcate,
            # tags = tags,
            stats = statslist,
            ares = areslist,
            # cateids = cateids,
            fh = videname,
            disklist = disklist,
            uuid = searchuuid
        )


#????????????
@auth.route('/video_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_video(id):
    video = Movie.query.get_or_404(id)
    # form = MovieForm()
    sett = SettingController().get_settings()
    form = MovieForm(
        stats=['0'],
        ares=['0'],
        splitfile = sett.splitfile,
        isperview = sett.perview,
        ismove = sett.cpOrmv
    )
    control = VideoController()
    pre_url = ''
    if request.referrer:
        arg = re.search('\?.*=.*',request.referrer)
        if arg:
            session['referrer'] = request.referrer

    if form.validate_on_submit():

        pre_url = session.pop('referrer', url_for('auth.list_video'))
        control.del_all_actors(video)
        control.del_all_tag(video)
        videoobj = control.video_bind_data(form,vid=id)

        if form.movieurl.data:

            #????????????????????????????????????
            # queue = MessageList.query.filter_by(name=form.bsname.data).all()
            # if queue:
            #     flash(u'???????????????????????????????????????????????????????????????','err')
            #     return redirect(url_for('auth.edit_video', id=id))

            videofile_controller = VideoFileController(disklist)
            video_file = videofile_controller.add_video_file(videoobj,form.movieurl.data)
            video_file.video= videoobj
            video.uuid = video_file.part_uuid
            db.session.add(video_file)
            db.session.commit()
            db.session.refresh(video_file)
            db.session.expunge(video_file)
            appcontext = current_app._get_current_object()
            #??????????????????
            videofile_controller.async_option_video_file(appcontext,video_file, form.movieurl.data)
        
        return redirect(pre_url)



    control.form_bind_data(video, form)

    filelist = video.video_files.all()
    flash(form.errors)
    return render_template('auth/movie_add.html', form=form, filelist=filelist)


#??????????????????
@auth.route('/restore_file/<int:id>', methods=['GET', 'POST'])
@login_required
def restore_file(id):
    try:
        file = VideoFile.query.get_or_404(id)
        control = VideoFileController(disklist)
        #?????????????????????????????????
        #???????????????
        st = control.check_message(file)
        if st:
            raise VideoFile(u'??????????????????????????????????????????')
        appcontext = current_app._get_current_object()
        db.session.refresh(file)
        db.session.expunge(file)
        control.async_option_video_file_other(control.async_restore_file,[appcontext,file])
        file = VideoFile.query.get_or_404(id) 
        file.parting=False
        db.session.add(file)
        db.session.commit()
        return redirect(url_for('auth.list_video'))
    except Exception as e:
        flash(str(e))
        return  redirect(request.referrer)


#??????????????????
@auth.route('/parting_file/<int:id>', methods=['GET', 'POST'])
@login_required
def parting_file(id):
    try:
        file = VideoFile.query.get_or_404(id)
        control = VideoFileController(disklist)
        #?????????????????????????????????
        #???????????????
        st = control.check_message(file)
        if st:
            raise ValueError(u'??????????????????????????????????????????')
        appcontext = current_app._get_current_object()
        db.session.refresh(file)
        db.session.expunge(file)
        control.async_option_video_file_other(control.async_parting_file,[appcontext,file])
        file = VideoFile.query.get_or_404(id)   
        file.physical_path = file.get_config_dir()
        file.parting=True
        db.session.add(file)
        db.session.commit()
        return redirect(url_for('auth.list_video'))
    except Exception as e:
        flash(str(e))
        return redirect(request.referrer)

#????????????????????????
@auth.route('/preview_file/<int:id>', methods=['GET', 'POST'])
@login_required
def preview_file(id):
    file = VideoFile.query.get_or_404(id)
    #?????????????????????????????????
    #???????????????
    if file.parting:
        raise ValueError(u'????????????????????????????????????')
    control = VideoFileController(disklist)
    appcontext = current_app._get_current_object()
    db.session.refresh(file)
    db.session.expunge(file)
    control.async_option_video_file_other(control.async_create_preview,[appcontext,file])
    file = VideoFile.query.get_or_404(id)   
    file.prew=True
    db.session.add(file)
    db.session.commit()
    return redirect(url_for('auth.list_video'))


#????????????????????????????????????
@auth.route('/removefile/<int:id>', methods=['GET','POST'])
@login_required
def removefile(id):
    file = VideoFile.query.get_or_404(id)
    if not file:
        raise ValueError(u'???????????????')
    videoid= file.video_id
    control = VideoFileController(disklist)
    appcontext = current_app._get_current_object()
    db.session.refresh(file)
    db.session.expunge(file)
    control.async_option_video_file_other(control.async_remove_video_file, [appcontext, file, False])
    file = VideoFile.query.get_or_404(id)
    db.session.delete(file)
    db.session.commit()
    
    return redirect(url_for('auth.edit_video',id=videoid))

#?????????????????????????????????????????????
@auth.route('/deletefile/<int:id>', methods=['GET','POST'])
@login_required
def deletefile(id):
    file = VideoFile.query.get_or_404(id)
    if not file:
        raise ValueError(u'???????????????')
    videoid= file.video_id
    control = VideoFileController(disklist)
    control.del_video_file(file)
    db.session.delete(file)
    db.session.commit()
    
    return redirect(url_for('auth.edit_video',id=videoid))

#????????????
@auth.route('/video_del/<int:id>/<int:dmodel>', methods=['GET', 'POST'])
@login_required
def delete_video(id, dmodel):
    video = Movie.query.get_or_404(id)
    video_files = video.video_files.all()
    control = VideoFileController(disklist)
    appcontext = current_app._get_current_object()
    for file in video_files:
        db.session.refresh(file)
        db.session.expunge(file)
        if dmodel:
            control.async_option_video_file_other(control.async_remove_video_file, [appcontext, file, True])
        else:
            control.async_option_video_file_other(control.async_remove_video_file, [appcontext, file, False])
        file = VideoFile.query.get_or_404(file.id)
        db.session.delete(file)
    video.remove_actor()
    video.remove_tag()
    video.remove_imgandvideo(disklist)
    db.session.delete(video)
    db.session.commit()
    return redirect(request.referrer)


@auth.route('/file/upload', methods=['POST'])
def upload_part():  # ?????????????????????????????????
    task = request.form.get('task_id')  # ??????????????????????????????
    chunk = request.form.get('chunk', 0)  # ??????????????????????????????????????????
    filename = '%s%s' % (task, chunk)  # ?????????????????????????????????

    uploadfile = request.files['file']
    upload_file(uploadfile,fname=filename)


    

    # upload_file.save(r'D:\code\mcms\app\static\upload\%s' % filename)  # ?????????????????????
    return render_template('auth/index.html')

@auth.route('/file/merge', methods=['GET'])
def upload_success():  # ?????????????????????????????????????????????
    target_filename = request.args.get('filename')  # ??????????????????????????????
    task = request.args.get('task_id')  # ??????????????????????????????
    basepath = make_path(current_app.config['UPLOADED_FILES_DEST'])
    file_pre = target_filename.split('.')[0]
    filetype ='.'+ target_filename.split('.')[-1]
    extend_num = 1
    while True:
        if check_dir_file(os.path.join(basepath, target_filename)):
            extend_name = str(extend_num)
            target_filename = file_pre + extend_name + filetype
            extend_num +=1
        else:
            break
    # tfilename = os.path.join(basepath, target_filename)
    # target_filename= tfilename.replace('\\','_')
    target_filename = os.path.join(basepath, target_filename)
    chunk = 0  # ????????????
    with open(target_filename, 'wb') as target_file:  # ???????????????
        while True:
            try:
                # filename = r'D:\code\mcms\app\static\upload\%s%d' % (task, chunk)
                filename = (basepath+'\\{}{}').format(task, chunk)
                source_file = open(filename, 'rb')  # ????????????????????????
                target_file.write(source_file.read())  # ?????????????????????????????????
                source_file.close()
            except IOError as msg:
                break

            chunk += 1
            os.remove(filename)  # ??????????????????????????????

    url = physical2URL(target_filename)
    newurl = '/video' + url


    return jsonify({'uploadfile': newurl })



@auth.route('/check', methods=['POST'])
def check_name():
    fh = request.form.get('fh')
    fh = fh.upper()
    if fh:
        video = Movie.query.filter_by(name=fh).first()
        if video:
            message = video.name
            vid = video.id
        else:
            message = '??????????????????'
            vid = -1
    else:
        message = '???????????????'
        vid = -1

    return jsonify({'data':message, 'id': vid})


@auth.route('/changestats', methods=['GET'])
@login_required
def cgstats():
    sid = request.args.get('id')
    stats = request.args.get('stats')
    if sid is None or stats is None:
        raise 'err'
    video = Movie.query.get_or_404(int(sid))
    if video is None:
        raise 'err'
    video.stats = int(stats)
    db.session.add(video)
    db.session.commit()
    return jsonify({'status':'True'})


@auth.route('/restore/<path:name>', methods=['GET'])
def restore_video(name):
    
    name = '/' + name

    hashpath = readfilePath(name)
    config = configparser.ConfigParser()
    config.read(hashpath)
    bname = config['Default']['name']
    dname = config['Default']['dir']
    filename = os.path.join(dname,bname)
    chumk = 0
    with open(filename, 'wb') as fr:
        while True:
            try:
                pdfile = hashpath + '{0}'.format(chumk)
                source_file = open(pdfile,'rb')
                fr.write(source_file.read())
                source_file.close()
                os.remove(pdfile)
            except IOError as e:
                break
            chumk += 1
    return jsonify({'data':'succes'})


@auth.route('/playgroup', methods=['GET'])
def play_group():
    playgroup = session.get('playgroup',[])

    parm = []
    for i  in playgroup:
        parm.append(Movie.id==int(i))
    if parm:
        v = Movie.query.filter(*parm)

        videos  = Movie.query.filter(or_(*parm)).all()
    else:
        videos = []
    return render_template('auth/playgroup.html', 
            movielist = videos,
            pygroup = 'true',
            disklist = disklist
        )


@auth.route('/addplay', methods=['GET'])
def add_play():
    vid = request.args.get('id')
    if not vid:
        raise "err"
    video  = Movie.query.get_or_404(int(vid))
    playgroup = session.get('playgroup',None)
    if playgroup is None:
        session['playgroup'] = [video.id]
    else:
        for i in playgroup:
            if video.id == i:
                break
        else:
            playgroup.append(video.id)
            session['playgroup'] = playgroup
    return jsonify({'data':'sucess'})


@auth.route('/delplay', methods=['GET'])
def del_play():
    vid = request.args.get('id')
    if not  vid:
        raise  'err'
    playgroup = session.get('playgroup',None)
    if playgroup:
        for i in  playgroup:
            if int(vid) == i:
                playgroup.remove(i)
        session['playgroup'] = playgroup
    return jsonify({'data':'sucess'})


@auth.route('/disks', methods=['GET', 'POST'])
def diskshow():
    form = DiskForm()
    diskdata = get_fs_info()
    # drive = Diskdrive()
    if form.validate_on_submit():
        control = Diskcontroller(disklist)
        disk = control.obj_bind(form)
        db.session.add(disk)
        db.session.commit()
        return redirect(url_for('auth.diskshow'))
    disks = Diskdb.query.all()
    for dk in disks:
        for rdisk in diskdata:
            uuid = rdisk['DeviceID']
            if uuid == dk.uuid:
                dk.FreeSize = float(rdisk['freesize'])
                diskdata.remove(rdisk)
                break
    print(form.errors)
    return render_template('auth/control.html', form=form, diskdata=diskdata, disks=disks)


@auth.route('/cgstatus/<int:id>', methods=['GET'])
def cgstatus(id):
    part = Diskdb.query.get_or_404(id)
    if part:
        localpart = Diskdb.query.filter_by(Status=True).first()
        if localpart:
            localpart.Status = False
            db.session.add(localpart)
        part.Status = True
        db.session.add(part)
        db.session.commit()
    return redirect(url_for('auth.diskshow'))



@auth.route('/deldisk/<int:id>', methods=['GET'])
def deldisk(id):
    part = Diskdb.query.get_or_404(id)
    try:
        db.session.delete(part)
        db.session.commit()
    except Exception as e:
        flash('????????????,????????????????????????????????????','err')
    return redirect(url_for('auth.diskshow'))


@auth.route('/setting', methods=['GET','POST'])
def setting():
    form = SettingForm()
    sets = SettingController().get_settings()
    if form.validate_on_submit():
        print(form.preview.data)
        sets.cpOrmv = form.cpOrmv.data
        sets.splitfile = form.splitfile.data
        sets.show = form.show.data
        sets.perview = form.preview.data
        db.session.add(sets)
        db.session.commit()
        flash(u'????????????','success')
        return redirect(url_for('auth.setting'))

    form.splitfile.data = sets.splitfile
    form.cpOrmv.data = sets.cpOrmv
    form.show.data = sets.show
    form.preview.data = sets.perview
    return render_template('auth/setting.html', form= form)


@auth.route('/othersoft', methods=['GET'])
def othersoft():
    '''
    ?????????????????????????????????
    '''
    path = request.args.get('path')
    if path:
        u = parse.unquote(path)
        file = findPhysical(u)
        if file:
            os.startfile(file)
    return jsonify({'data':'true'})



    
@auth.route('/ajaxdata', methods=['GET'])
def ajaxdata():
    dir_id = request.args.get('id')
    uen_path = parse.unquote(dir_id)
    msg_list =[]
    children = []
    data_dict = {}
    if uen_path == '#':
        session_status = session.get('rootpath',None)
        if session_status is not None:
            msg_list = session['rootpath']
        else:
            disk_part = get_fs_info()
            for disk_mg in disk_part:
                data_path = {}
                data_path['text'] = disk_mg['Caption']
                data_path['icon'] = 'folder'
                data_path['children'] = True
                data_path['id'] = parse.quote(disk_mg['Caption']+'\\')
                children.append(data_path)
            data_dict['text'] = 'root'
            data_dict['icon'] = 'folder'
            data_dict['children'] = children
            data_dict['id'] = '#'
            data_dict['state'] = {
                'disabled':True,
                'opened':True
            }
            msg_list.append(data_dict)
            session['rootpath'] = msg_list

    else:
        if os.path.isdir(uen_path):
            paths = os.listdir(uen_path)
            if paths:
                for  path in paths:
                    data_path = {}
                    fullpath = os.path.join(uen_path,path)
                    if os.path.basename(fullpath) == 'System Volume Information' or os.path.basename(path) == '$RECYCLE.BIN':
                        continue
                    if os.path.isdir(fullpath):
                        data_path['children'] = True
                        data_path['icon'] = 'folder'

                    else:
                        data_path['children'] = False
                        data_path['icon'] = 'file file-php'
                        data_path['type'] = 'file'
                    data_path['text'] = path
                    data_path['id'] = parse.quote(fullpath)
                    children.append(data_path)
                data_dict['children'] = children
                data_dict['icon'] = 'folder'
                data_dict['text'] = os.path.basename(uen_path) if os.path.basename(uen_path) else uen_path.split('\\')[0]
                data_dict['id'] = dir_id
                msg_list.append(data_dict)
    return jsonify(msg_list)



@auth.route('/actor/<int:id>', methods=['GET','POST'])
def showactor(id):
    actor = Actor.query.get_or_404(id)
    mp = Myphoto.query.filter_by(actorid=actor.id).first()
    # print(actor.description)
    return render_template('milf.html', actor=actor, mp=mp)


        


@auth.route('/getvideomg', methods=['GET'])
def getvideomg():
    keyword = request.args.get('keyword')
    # url='http://www.javlibrary.com/cn/vl_searchbyid.php?&keyword={0}'
    # url = 'http://www.b47w.com/cn/vl_searchbyid.php?&keyword={0}'
    if not keyword:
        raise('err')
    # target = url.format(keyword)
    # a = javlib_search_video_msg(keyword)
    
    try:
        # raise ValueError(u'??????????????????')
        source = [JavDbModeController(),JavBusModeController()]
        for controll in source:
            md = controll.search_video_message(keyword)
            if md:
                break
        else:
            raise ValueError(u'??????????????????')
        v_dist = {
                'title': md.title,
                'no': md.fanhao,
                'tags': md.get_tags_nourl(),
                'actors': md.get_actors_nourl() if md.get_actors_nourl() else 'N/A',
                'img': md.samle_img,
                'cate': md.fanhao.split('-')[0],
                'date': md.dtime,
                'director': md.get_daoyan_nourl(),
                'producer':md.get_pianshang_nourl(),
                'series': md.get_xilie_nourl()
        }

        return jsonify(v_dist)
    except Exception as e:
        v_dist = {"readyState":0,"status":0,"statusText":"error"}
        print('????????????')
        return jsonify(v_dist)
        

@auth.route('/readmg', methods=['GET'])
def readmg():
    queues = [x.name for x in MessageList.query.all()]

    return jsonify({'data':queues})

@auth.route('/list_task', methods=['GET'])
def list_task():
    mid = request.args.get('id')
    if mid:
        mgmode = MessageList.query.filter_by(id=mid).first()
        if mgmode:
            restoretask(mgmode.path)
            flash('{0}.????????????....'.format(mgmode.name),'info')
            return redirect(url_for('auth.list_task'))

    mglist = MessageList.query.all()
    return render_template('auth/tast.html', mglist=mglist)




@auth.route('/showfollow', methods=['POST','GET'])
def showfollow():
    vdf = VdFollow.query.order_by(VdFollow.status.desc()).all()
    return render_template('auth/follow.html',vdf=vdf)


@auth.route('/create_perview_img', methods=['GET'])
@login_required
def create_perview_img():
    video_id = request.args.get('id')
    if not video_id:
        raise 'err'
    video = Movie.query.get_or_404(int(video_id))
    if not video:
        raise 'err'
    disk = disklist.get(video.uuid, None)
    if disk is None:
        raise 'err'
    pyfile = '{}{}'.format(disklist.get(video.uuid),video.pypath)
    hashpath = '{}{}'.format(disk, video.hashpath)
    perview_restorefile(video.id,pyfile,hashpath)
    return redirect(url_for('main.show',id=video.id))



@auth.route('/test', methods=['GET'])
def test():

    # from lxml import etree
    # import requests

    # headers = {
    #         'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'
    #     }

    # url = 'https://www.javbus.com/OKSN-325'
    # url = 'https://www.javbus.com/DASD-834'
    # from ..lib.javbus import JavBusModeController
    # javbus = JavBusModeController()
    # md = javbus.search_video_message('JUL-515')
    # if md:
    #     print(
    #         md.fanhao,
    #         md.title,
    #         md.samle_img,
    #         md.dtime,
    #         md.pianshang,
    #         md.faxing,
    #         md.tags,
    #         md.actors,
    #         md.daoyan,
    #         md.xilie
    #         )

    return render_template('test.html')




#----------------------????????????----------------------------------------------------

@auth.route('/zimulist', methods=['GET'])
def list_zimu():

    page = request.args.get('page', 1, type = int)
    st = time.time() * 1000
    pagination = Zimu.query.order_by(Zimu.id.desc()).paginate(
        page, per_page = current_app.config['CATEGORY_PER_PAGE'],
        error_out = False
    )


    movielist = pagination.items


    rti = time.time() * 1000 - st

    return render_template('auth/zimu_list.html', 
            movielist = movielist,
            pagination = pagination,
            disklist = disklist

        )



@auth.route('/zimu_add', methods=['GET','POST'])
@login_required
def zimu_add():
    form = ZimuForm()
    if form.validate_on_submit():
        zimu = Zimu(
            name = form.name.data,
            title = form.title.data,
            img = checkimgurl(form.imgurl.data),
        )
        zimu.path = os.path.basename(form.movieurl.data)
        db.session.add(zimu)
        db.session.commit()
        if not os.path.exists(zimu.hashpath):
            os.makedirs(zimu.hashpath)
        aysc_init_zimu_img(zimu.id,form.movieurl.data,zimu.hashpath)
        return redirect(url_for('auth.list_zimu'))
    return render_template('auth/zimu_add.html', form=form)

@auth.route('/zimu_del/<int:id>', methods=['GET','POST'])
@login_required
def zimu_del(id):
    zm = Zimu.query.get_or_404(id)
    if zm.zivalues:
        zv = ZimuValue.query.filter_by(pid=zm.id).all()
        for z in zv:
            db.session.delete(z)
    db.session.delete(zm)
    if os.path.exists(zm.hashpath):
        shutil.rmtree(zm.hashpath)
    return redirect(url_for('auth.list_zimu'))
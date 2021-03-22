from flask import render_template, redirect, request, url_for, flash, current_app, send_from_directory, jsonify, Response
from . import main
from ..models import User, Category, Tag, Actor, Movie, Movie2Actor, Movie2Tag, VideoTime, Myphoto, ImgTag, Photo2Tag, Zimu, ZimuValue, VideoFile, Diskdb
from flask_login import login_user, current_user, login_required
from .. import  db, disklist
import re
from ..lib.opfile import URL2physical, upload_base64, hash_file_name, create_config_file, splitfile, get_PARTITIONS, time2int
import datetime
import os
import configparser
import time
from  sqlalchemy.sql.expression import func
# from ..lib.javbus import make_request, get_list_mgs, get_movie_mg
from ..lib.javdb import JavDbModeController
import json
import shutil
from ..controller.videocontroller import VideoController
from ..controller.videofilecontroller import VideoFileController

@main.route('/', methods=['GET',"POST"])
def index():
    return redirect(url_for('auth.list_video'))



@main.route('/show/<id>', methods=['GET','POST'])
@login_required
def show(id):
    idlist = str(id).split('_')
    viewimg = []
    video = Movie.query.get_or_404(int(idlist[0]))
    video.namehtml = '<a href={}>{}</a>-{}'.format(
            url_for('auth.list_video', cate=video.category.id),
            video.category.name,
            video.name.split('-')[-1]
            )
    if len(idlist)< 2:
        video_file = video.video_files.order_by(VideoFile.id).first()
    else:
        video_file = VideoFile.query.get_or_404(int(idlist[1]))
    try:
        filecontrol = VideoFileController(disklist)
        if not video_file:
            raise ValueError(u'没有视频文件')
        if video_file.prew:
            viewimg = filecontrol.read_viewimg_json(video_file)
        video_files = video.video_files.order_by(VideoFile.id).all()
        
        video.videopath = filecontrol.get_video_file_path(video_file)

        #-----------------------------字幕----------------
        rootpath = r'D:\code\mcms\app\static\upload\perview\file'
        ziname = video.name
        fullpath = '{}\\{}.vtt'.format(rootpath, ziname)
        
        print(video.namehtml)
        zimu = None
        if os.path.exists(fullpath):
            video_file.zimu = '/static/upload/perview/file/{}.vtt'.format(ziname)

    except ValueError:
        flash(u'没有视频文件','err')
        return redirect(request.referrer)
    except IOError:
        diskdb = Diskdb.query.filter_by(uuid=video_file.part_uuid).first()
        if diskdb:
            video.diskalise = diskdb.AliseName
        else:
            video.diskalise = ''

    return render_template('video.html', 
                video=video, 
                jdata = viewimg,
                video_file = video_file,
                video_files = video_files
                )

#读取预览图
@main.route('/img/<path:name>',methods=['GET'])
def img_show(name):
    vid = name.split('/')[-1].split('_')[0]
    vname = name.split('/')[-1].split('_')[-1]
    video = VideoFile.query.get_or_404(vid)
    filecontrol = VideoFileController(disklist)
    #读取预览图片返回流
    imgstream = filecontrol.read_preview(video, vname)
    headers = {
        'Content-Length': len(imgstream),
        'Content-Type' : 'image/jpeg',
    }
    return Response(imgstream, 200, headers=headers)



#读取视频文件
@main.route('/video/<int:vid>', methods=['GET'])
def printvideo(vid):
    range_header = request.headers.get('Range', None)
    file = VideoFile.query.get_or_404(vid)
    filecontrol = VideoFileController(disklist)
    chunk, status, headers = filecontrol.read_video_file_steam(file, range_header)
    return Response(chunk, status, headers=headers)


@main.route('/videoshow', methods=['GET','POST'])
def vshow():
    pass


#添加视频看点。
@main.route('/wdf_add', methods=['POST'])
def add_wdf():
    img = request.form.get('imgurl')
    tm = request.form.get('wdtime')
    wd_id = request.form.get('id')

    if not img or not tm or not wd_id:
        raise 'err'
    video_file = VideoFile.query.get(int(wd_id))
    img = upload_base64(img)
    if not video_file:
        raise 'err'
    try:
        votime = VideoTime(
            imgurl = img,
            time = float(tm)
        )
        votime.video_file = video_file
        db.session.add(votime)
        db.session.commit()
    except Exception as e:
        # print('sfsdfsdf')
        raise str(e)
    showtime = str(datetime.timedelta(seconds=float(tm)))

    return jsonify({'imgurl':votime.imgurl, 'wdtime':votime.time, 'showtime':showtime, 'id':votime.id})


@main.route('/wdf_del', methods=['GET'])
def del_wdf():
    wid = request.args.get('id')
    if wid is None:
        raise 'err'
    vt = VideoTime.query.filter_by(id=int(wid)).first()
    if vt is None:
        raise 'err'
    try:
        db.session.delete(vt)
        db.session.commit()
    except Exception as e:
        raise 'err'
    return jsonify({'id': wid})


@main.route('/show_img/<int:id>' ,methods=['GET'])
@login_required
def show_img(id):
    photo = Myphoto.query.get_or_404(id)
    tags =  db.session.query(ImgTag).select_from(Photo2Tag).filter_by(photo_id=photo.id).join(ImgTag, Photo2Tag.tag_id==ImgTag.id)
    return render_template('img.html', photo=photo,  tags=tags, imgs=photo.Imgs)


    


@main.route('/index', methods=['GET','POST'])
@login_required
def mbindex():
    banner = Movie.query.filter(Movie.stats >= 3).order_by(Movie.stats.desc(), func.rand()).limit(5)
    renqi = db.session.query(Movie).select_from(Movie2Tag).filter_by(tag_id=25).join(
                Movie, Movie2Tag.movie_id==Movie.id).order_by(Movie.stats.desc(), func.rand()).limit(4)
    shunv = db.session.query(Movie).select_from(Movie2Tag).filter_by(tag_id=3).join(
                Movie, Movie2Tag.movie_id==Movie.id).order_by(Movie.stats.desc(), func.rand()).limit(4)
    shaonv = db.session.query(Movie).select_from(Movie2Tag).filter_by(tag_id=11).join(
                Movie, Movie2Tag.movie_id==Movie.id).order_by(Movie.stats.desc(),func.rand()).limit(4)

    tags = Tag.query.all()
    cateids = Category.query.all()
    return render_template('mbindex.html', 
                banner = banner, 
                renqi = renqi, 
                shunv = shunv, 
                shaonv = shaonv,
                tags = tags,
                cateids = cateids)



@main.route('/mobieshow/<int:id>', methods=['GET'])
def mbshow(id):
    # video = Movie.query.get_or_404(id)
    tags = db.session.query(Tag).select_from(Movie2Tag).filter_by(movie_id=id).join(Tag, Movie2Tag.tag_id==Tag.id)
    # actors = video.re
    # tags = video.readTags()
    sjshu = int(round(time.time()*1000)) % tags.count()

    t_id = tags[sjshu].id
    videos = db.session.query(Movie).select_from(Movie2Tag).filter_by(tag_id=t_id).join(Movie, Movie2Tag.movie_id==Movie.id).order_by(func.rand()).limit(5)

    idlist = str(id).split('_')
    viewimg = []
    video = Movie.query.get_or_404(int(idlist[0]))
    if len(idlist)< 2:
        video_file = video.video_files.order_by(VideoFile.id).first()
    else:
        video_file = VideoFile.query.get_or_404(int(idlist[1]))
    try:
        filecontrol = VideoFileController(disklist)
        if not video_file:
            raise ValueError(u'没有视频文件')
        if video_file.prew:
            viewimg = filecontrol.read_viewimg_json(video_file)
        video_files = video.video_files.order_by(VideoFile.id).all()
        
        video.videopath = filecontrol.get_video_file_path(video_file)

    except ValueError:
        flash(u'没有视频文件','err')
        return redirect(request.referrer)
    except IOError:
        diskdb = Diskdb.query.filter_by(uuid=video_file.part_uuid).first()
        if diskdb:
            video.diskalise = diskdb.AliseName
        else:
            video.diskalise = ''

    return render_template('mbvideo.html', 
                video=video, 
                jdata = viewimg,
                video_file = video_file,
                video_files = video_files,
                videos = videos
                )

@main.route('/video_mlist', methods=['GET', 'POST'])
@login_required
def mlist_video():
    page = request.args.get('page', 1, type = int)
    searchtag = request.args.get('tag')
    searchactor = request.args.get('actor')
    searchcate = request.args.get('cate')
    statslist = request.args.get('stats')
    areslist = request.args.get('ares')
    videname = request.args.get('fh')

    videoquery = Movie.query
    if searchtag:
        videoquery = db.session.query(Movie).select_from(Movie2Tag).filter_by(tag_id=int(searchtag)).join(
                        Movie, Movie2Tag.movie_id==Movie.id)

    if searchactor:
        videoquery = db.session.query(Movie).select_from(Movie2Actor).filter_by(actor_id=int(searchactor)).join(
                        Movie, Movie2Actor.movie_id==Movie.id)

    if searchcate:
        videoquery = Movie.query.filter_by(cate_id=int(searchcate))

    if statslist:
        # videoquery = Movie.query.filter_by(stats=int(statslist))
        videoquery = Movie.query.filter(Movie.stats >= int(statslist)).order_by(Movie.stats.desc())


    if areslist:
        videoquery = Movie.query.filter_by(ares=int(areslist))

    if videname:
        videoquery = Movie.query.filter(Movie.name.like('%'+ videname + '%'))

    pagination = videoquery.order_by(Movie.id.desc()).paginate(
        page, per_page = current_app.config['CATEGORY_PER_PAGE'],
        error_out = False
    )
    tags = Tag.query.all()
    cateids = Category.query.all()
    movielist = pagination.items
    return render_template('mbsearch.html', 
            movielist = movielist,
            pagination = pagination,
            tagid = searchtag,
            actorid = searchactor,
            cid = searchcate,
            tags = tags,
            stats = statslist,
            ares = areslist,
            cateids = cateids,
            fh = videname
        )
# @main.route('/cv', methods=['GET'])
# @login_required
# def change_video():
#     file = r'J:\video\2020\6\27\FC2PPV-1035407.mp4'
#     splitfile(file)


#     return redirect(url_for('auth.list_video'))


# @main.route('/javbuslist', methods=['GET'])
# def javbuslist():
#     html = {}
#     url = 'https://www.javbus.com/'
#     pg = request.args.get('page')
#     if pg:
#         url = 'https://www.javbus.com/page/{0}'.format(pg)
#     res = make_request(url)
#     if res:
#         html = get_list_mgs(res)
#     return render_template('javbuslist.html', javbusmg = html)


# @main.route('/javbus/<name>', methods=['GET'])
# def javbus(name):
#     url = 'https://www.javbus.com/{0}'.format(name)
#     pg = make_request(url)
#     html = get_movie_mg(pg, url)
#     return render_template('javbus.html', javbusmg = html)

# @main.route('/javdb', methods=['GET'])
# def javdb():
#     url = 'https://javdb.com/'
#     reargs = request.full_path
#     if reargs:
#         reargs = reargs.replace('/javdb','')
#         print(reargs)
#         url = 'https://javdb.com/{}'.format(reargs)
    
#     print(url)
#     req = make_javdb_request(url)
#     htmldoc = get_list_content(req)
#     pages = get_video_pages(req)
#     return render_template('javdblist.html', javdbmode=htmldoc, pages=pages)

# @main.route('/javdb/v/<name>', methods=['GET'])
# def javdbshow(name):
#     url = 'https://javdb.com/v/{}'.format(name)
#     req = make_javdb_request(url)
#     md = get_show_main(req)
#     md.uid = name
#     return render_template('javdb.html', javdbmd=md)

# @main.route('/follow', methods=['GET'])
# def follow_video():
#     uid = request.args.get('uid')
#     if uid:
#         url = 'https://javdb.com/v/{}'.format(uid)
#         req = make_javdb_request(url)
#         md =get_show_main(req)
#         vf = VdFollow(
#             name = md.fanhao,
#             link = url,
#             img = md.samle_img,
#             title = md.title,
#         )
#         db.session.add(vf)
#         db.session.commit()
#         flash('关注成功','success')
#     else:
#         flash('关注失败','err')
#     return redirect(url_for('main.javdbshow', name=uid))

# @main.route('/flist', methods=['GET','POST'])
# def follow_show():
#     fms = VdFollow.query.all()
#     return render_template('follow.html',fms=fms)

# @main.route('/del_follow', methods=['GET'])
# @login_required
# def del_follow():
#     fid = request.args.get('id')
#     vf = VdFollow.query.filter_by(id=fid).first()
#     if vf:
#         db.session.delete(vf)
#         db.session.commit()
#     return redirect(url_for('main.follow_show'))

# @main.route('/img/1', methods=['GET'])
# def img_show():
#     localfile = r'D:\code\mcms\app\static\upload\image\zd.jpg'
#     fsize = os.path.getsize(localfile)
#     with open(localfile, 'rb') as fr:
#         imgstream = fr.read()
#     headers = {
#         'Content-Length': fsize,
#         'Content-Type' : 'image/jpeg',
#     }
#     return Response(imgstream, 200, headers=headers)

#-----------------------------字幕----------------------------
@main.route('/zmshow/<int:id>', methods=['GET','POST'])
@login_required
def zmshow(id):
    video = Zimu.query.get_or_404(id)
    video.local = 0
    video.pre = 0
    video.next = 1
    video.skip = 0
    if video.skiptime:
        video.skip = video.skiptime
    zivaule = video.zivalues.order_by(ZimuValue.xuhao.desc()).all()
    if zivaule:
        video.local = int(zivaule[0].xuhao)
        video.pre = video.local -1
        video.next = video.local + 1
        video.perview = '{}/{}.jpg'.format(video.path, video.local)
    return render_template('zimushow.html', video=video, zimulist=zivaule )


@main.route('/imgpage', methods=['GET','POST'])
@login_required
def imgpage():
    prid = request.args.get('id')
    page = int(request.args.get('page'))
    print(page)
    video = Zimu.query.get_or_404(prid)
    if video.checkfile(page):
        video.local = page
        video.pre = page - 1
        video.next = page + 1
        video.skip = 0
        video.preview = '{}/{}.jpg'.format(video.path, page)
        imgdict = {
            'localtime': video.timeformat(video.local),
            'local': video.local,
            'pre': video.pre,
            'next': video.next,
            'img': video.preview,
            'st': True
        }
        print(imgdict)
        return jsonify(imgdict)
    return jsonify({'st': False})


@main.route('/zivalue_add', methods=['GET','POST'])
@login_required
def zivalue_add():
    pid = request.args.get('pid')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    sort = request.args.get('sort')
    msg = request.args.get('msg')

    if pid and start_time and end_time and sort and msg:
        zi = Zimu.query.filter_by(id=pid).first()
        if zi:
            if int(start_time) <= int(end_time):
                zm = ZimuValue(
                    starttime = start_time,
                    endtime = end_time,
                    zmvalue = msg,
                    xuhao = int(sort)
                )
                zm.zimu = zi
                db.session.add(zm)
                db.session.commit()
                return jsonify({
                    'st':True,
                    'starttime': zi.timeformat(zm.starttime),
                    'endtime': zi.timeformat(zm.endtime),
                    'msg': zm.zmvalue,
                    'pid': zm.id
                    })
    
    return jsonify({'st':False})




@main.route('/create_zm_file/<int:id>', methods=['GET','POST'])
@login_required
def create_zm_file(id):
    zmid = Zimu.query.get_or_404(id)
    zmlist = zmid.zivalues.order_by(ZimuValue.xuhao).all()
    root = r'D:\code\mcms\app\static\upload\perview\file'
    path = '{}\\{}.vtt'.format(root, zmid.name)
    lines =['WEBVTT','\n','\n']
    for zl in zmlist:
        zmid.skiptime=0
        starttime = int(zl.starttime) - int(zmid.skiptime)
        endtime = int(zl.endtime) - int(zmid.skiptime)
        ts = '{} --> {}'.format(
            zmid.timeformat(starttime),
            zmid.timeformat(endtime)
            )
        lines.append(ts)
        lines.append('\n')
        lines.append(zl.zmvalue)
        lines.append('\n')
    with open(path, 'w+', encoding='utf-8') as fr:
        fr.writelines(lines)

    return redirect(url_for('main.zmshow',id=zmid.id))



@main.route('/set_skiptime', methods=['GET','POST'])
@login_required
def set_skiptime():
    zm_id = request.args.get('id')
    skiptime = request.args.get('skiptime')
    zm = Zimu.query.get_or_404(zm_id)
    zm.skiptime = int(skiptime)
    db.session.add(zm)
    db.session.commit()
    return jsonify({'skiptime': zm.timeformat(zm.skiptime)})

@main.route('/del_zmvalue', methods=['GET','POST'])
@login_required
def del_zmvalue():
    zd = request.args.get('id')
    if not zd:
        raise 'err'
    mz = ZimuValue.query.filter_by(id=zd).first()
    if not mz:
        raise 'err'
    db.session.delete(mz)
    db.session.commit()
    return jsonify({'id': mz.id})


@main.route('/zimu_comeplte/<int:id>', methods=['GET','POST'])
@login_required
def zimu_comeplte(id):
    zm = Zimu.query.get_or_404(zm_id)
    zm.status = True
    db.session.add(zm)
    if os.path.exists(zm.hashpath):
        shutil.rmtree(zm.hashpath)
    return url_for('main.zmshow',id=zm.id)

@main.route('/set_currenttime', methods=['GET'])
@login_required
def set_currenttime():
    file_id = request.args.get('file_id')
    currentime = request.args.get('currentime')
    if not file_id or not currentime:
        raise ValueError(u'err')
    videl_file = VideoFile.query.get(int(file_id))
    if not videl_file:
        raise ValueError(u'err')
    currentime = int(float(currentime))
    videl_file.currenttime = currentime
    db.session.add(videl_file)
    return jsonify({'status':True})






from . import img
from flask import render_template, redirect, request, url_for, flash, current_app, send_from_directory, jsonify, Response, session
from .forms import PhotoForm, Img_tagForm
from ..models import User, Category, Tag, Actor, Movie, Movie2Actor, Movie2Tag, ImgTag, Photo2Tag, Myphoto
from flask_login import login_user, current_user, login_required, logout_user
from .. import  db
from ..lib.opfile import upload_base64, Removechar, delfile
import re


#----------标签管理----------------


#添加标签
@img.route('/itag_add', methods=['GET', 'POST'])
@login_required
def Imgtag_Add():
    form = Img_tagForm()
    if form.validate_on_submit():
        cli = ImgTag(
            name = form.txtTitle.data,
            sortnum = form.txtSortId.data,
            
        )
        if not cli.check_name():
            flash('标签已存在')
            return redirect(url_for('img.Tag_Add'))
        db.session.add(cli)
        db.session.commit()
        return redirect(url_for('img.Imgtag_list'))
    return render_template('auth/img_tag_add.html',form=form)



@img.route('/itlist', methods=['GET','POST'])
@login_required
def Imgtag_list():
    page = request.args.get('page', 1, type = int)
    pagination = ImgTag.query.order_by(ImgTag.sortnum.desc()).paginate(
        page, per_page = current_app.config['CATEGORY_PER_PAGE'],
        error_out = False
    )
    taglist = pagination.items
    return render_template('auth/img_tag_list.html', 
            taglist = taglist,
            pagination = pagination
        )


#------标签修改-----
@img.route('/itag_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def imgedit_tag(id):
    tag = ImgTag.query.get_or_404(id)
    form = Img_tagForm()
    if form.validate_on_submit():
        tag.name = form.txtTitle.data
        tag.sortnum = form.txtSortId.data
        try:
            db.session.add(tag)
            db.session.commit()
            return redirect(url_for('img.Imgtag_list'))
        except Exception as e:
            flash('更新失败，检查标签是否重复')
            return redirect(url_for('img.imgedit_tag', id=id))
    form.txtTitle.data = tag.name
    form.txtSortId.data = tag.sortnum
    return render_template('auth/img_tag_add.html', form=form)

 #----标签删除-----
@img.route('/it_delete', methods=['GET','POST'])
@login_required
def imgtag_delete():
    if request.method == 'GET':
        tid = request.args.get('id')
        arr = [tid,]
    if request.method == 'POST':
        arr = request.values.getlist('checked_arry')
    if arr:
        for cid in arr:
            tag = ImgTag.query.filter_by(id=int(cid)).first()
            db.session.delete(tag)
        db.session.commit()
    return redirect(url_for('img.Imgtag_list'))



@img.route('/photo_add', methods=['GET','POST'])
@login_required
def add_photo():
    form = PhotoForm()
    if form.validate_on_submit():
        imgs_base64 = form.imgurls.data
        imgurls = ''
        if imgs_base64:
            pre = 0
            if imgs_base64.startswith('data:image'):
                imgs_base64 = imgs_base64.lstrip('data:image')
            for imgbase64 in imgs_base64.split('data:image'):
                img = 'data:image' + imgbase64
                imgurl = upload_base64(img,pre=str(pre))
                imgurl = imgurl + ';'
                imgurls = imgurls + imgurl
                pre = pre + 1

        mp = Myphoto(
            name = form.name.data,
            # imgurls = form.imgurls.data,
            Imgs = imgurls,
            stats = form.stats.data,
            actorid = form.actorid.data
        )
        db.session.add(mp)
        for it in form.tids.data:
            tag = ImgTag.query.filter_by(id=int(it)).first()
            pt = Photo2Tag(photos=mp, tags=tag)
            db.session.add(pt)
        db.session.commit()
        flash('添加成功')
        return redirect(url_for('img.add_photo'))
    
    return render_template('auth/photo_add.html',form=form)


@img.route('/photo_list', methods=['GET','POST'])
def list_photo():
    page = request.args.get('page', 1, type = int)
    pagination = Myphoto.query.order_by(Myphoto.stats.desc(),Myphoto.id.desc()).paginate(
        page, per_page = current_app.config['CATEGORY_PER_PAGE'],
        error_out = False
    )
    photolist = pagination.items
    return render_template('auth/photo_list.html',
            photolist = photolist,
            pagination = pagination
        )


@img.route('/photo_edit/<int:id>', methods=['GET','POST'])
def edit_photo(id):
    photo = Myphoto.query.get_or_404(id)
    form = PhotoForm()
    page = 1
    if request.referrer:
        arg = re.search('(?P<arg>page=)(?P<num>[0-9]+)',request.referrer)
        if arg:
            page = arg.group('num')
            session['page'] = page
    if form.validate_on_submit():
        page = session.pop('page','1')
        imgs_base64 = form.imgurls.data
        if imgs_base64:
            imgurls = ''
            pre = 0

            if imgs_base64.startswith('data:image'):
                imgs_base64 = imgs_base64.lstrip('data:image')
            for imgbase64 in imgs_base64.split('data:image'):
                img = 'data:image' + imgbase64
                imgurl = upload_base64(img,pre=str(pre))
                imgurl = imgurl + ';'
                imgurls = imgurls + imgurl
                pre = pre + 1
            photo.append_img(imgurls)
        photo.name = form.name.data
        photo.stats = form.stats.data
        photo.actorid = form.actorid.data

        try:
            for p in photo.tags:
                db.session.delete(p)
            for it in form.tids.data:
                tag = ImgTag.query.filter_by(id=int(it)).first()
                pt = Photo2Tag(photos=photo, tags=tag)
                db.session.add(pt)
            db.session.commit()
            return redirect(url_for('img.list_photo', page=page))
        except Exception as e:
            flash('更新失败')
            return redirect(url_for('img.edit_photo)', id=id))
    form.name.data = photo.name
    form.tids.data = [str(x.tag_id) for x in photo.tags.all()]
    form.stats.data = str(photo.stats)
    form.actorid.data = str(photo.actorid)
    imgslist = photo.Imgs
    return render_template('auth/photo_add.html', 
                form=form, 
                imgslist=imgslist,
                photo = photo
                )


@img.route('/img_del', methods=['GET','POST'])
def Del_img():
    p_id = request.form.get('id')
    p_img = request.form.get('img')
    if p_id is None or p_img is None:
        raise 'err'
    photo = Myphoto.query.get_or_404(int(p_id))
    photo.del_img(p_img)
    db.session.add(photo)
    db.session.commit()
    delfile(p_img)
    return jsonify({'data':'true'})


@img.route('/img_change', methods=['GET','POST'])
def img_change():
    p_id = request.form.get('id')
    p_img = request.form.get('img')
    if p_id is None or p_img is None:
        raise 'err'
    photo = Myphoto.query.get_or_404(int(p_id))
    photo.change_img(p_img)
    db.session.add(photo)
    db.session.commit()
    return jsonify({'data':'true'})


@img.route('/photo_del', methods=['GET','POST'])
def del_photo():
    if request.method == 'GET':
        photo_id = [request.args.get('id'),]
    if request.method == 'POST':
        photo_id = request.values.getlist('checked_arry')
    if photo_id is None:
        return 'err'

    for pid in photo_id:
        p = Myphoto.query.filter_by(id=int(pid)).first()
        if p:
            try:
                p.remove_tag()
                arri = p.Imgs
                db.session.delete(p)
                db.session.commit()
                for i in arri:
                    delfile(i)
            except Exception as e:
                flash('删除出错了')
    return redirect(url_for('img.list_photo'))
            
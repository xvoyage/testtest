from flask import request, current_app, session
import os
from datetime import datetime
import time
import base64
import re
import sys
import shutil
import threading
import hashlib
import configparser
import pythoncom
import wmi
from ..models.disk import Diskdb
from ..models.settings import Settings
from ..models.message import MessageList
# from ..models.other import Zimu, ZimuValue
from flask_sqlalchemy import SQLAlchemy
from .. import db
# from  .messagequeue import MessageQueue
from .. import qe
import cv2
import numpy


#------获取配置文件------
def get_PARTITIONS():
    '''
        获取所有分区文件存放位置
    '''
    return [x.Path for x in Diskdb.query.all()]

def get_UPLOADED_FILES_DEST():
    '''
        获取当前上传文件的目标存放位置
    '''
    part = Diskdb.query.filter_by(Status=True).first()
    if part:
        return part.uuid
    return False

def get_COPY_FILE_DES():
    '''
        获取预设的源文件存放路径
    '''
    st = Settings.query.first()
    return st.source_dir

#---------------end-------------------------


# 生成缩略图
def resize_image(image, height=102, width=180):
    top, bottom, left, right= (0,0,0,0)
    h, w, o = image.shape
    longest_edge = max(h,w)
    black = [0,0,0]
    constant = cv2.copyMakeBorder(image,top,bottom,left,right, cv2.BORDER_CONSTANT, value=black)
    return cv2.resize(constant,(width, height))

def save_img(image,addr,num):
    path = os.path.join(addr,'{}.jpg'.format(num))
    rsimg = resize_image(image)
    cv2.imwrite(path,rsimg,[cv2.IMWRITE_JPEG_QUALITY,100])


def create_zo_img(width=180, height=102):
    I=numpy.zeros((5*height,width*10),dtype=numpy.uint8)
    I=cv2.cvtColor(I,cv2.COLOR_GRAY2BGR)
    return I

def write_into_img(dicimg, srcimg, top,left,width, height):
    dicimg[top:top+height,left:left+width] = srcimg[0:height,0:width]
    return dicimg

def init_video_img(vid,video,imgpath, jg=1):
    dname = os.path.dirname(imgpath)
    if not os.path.exists(dname):
        os.makedirs(dname)
    qe.put([vid,0,0])
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
                img = create_zo_img()
            rsimg = resize_image(frame)
            write_into_img(img,rsimg,rows*102,coloums*180,180,102)
            line = '{0}.jpg#xywh={1},{2},180,102'.format(virpath.format(vid,j),coloums*180,rows*102)
            jilu.append(line)
            coloums += 1
        success, frame = cap.read()
    
    if img is not None:
        filename = imgpath + str(j) + '.jpg'
        cv2.imwrite(filename,img)
    qe.put([vid,100,1])
    return jilu

    #-----------------------------end---------------------------


def string2list(strs):
    if strs:
        return strs.split('|')
    return None

def list2string(lists):
    if lists:
        return '|'.join(lists)
    return None

def get_sesion_value(name):
    seson = session.get(name, None)
    if seson is None:
        return []
    return string2list(seson)

def set_sesion_value(name,value):
    arr = get_sesion_value(name)
    arr.append(value)
    sessionvalue = list2string(arr)
    session[name] = sessionvalue


def clean_sesion_value(name):
    seson = session.get(name, None)
    if seson:
        session.pop(name)

def allowed_file(filename):
    '''
        验证文件后缀是否符合要求。
        filename: 文件名
    '''
    extend = filename.split('.')[-1]
    file = current_app.config['UPLOADED_FILES']
    img  = current_app.config['UPLOADED_IMG']
    if extend in file:
        return get_UPLOADED_FILES_DEST()
    elif extend in img:
        return current_app.config['UPLOADED_PHOTOS_DEST']
    else:
        return None

def check_dir_file(filedir):
    return os.path.exists(filedir)


#-------有bug,文件上传会出错--------------
def physical2URL(path):
    '''
        绝对路径转相对路径
    '''
    extend = path.split('.')[-1]
    file = current_app.config['UPLOADED_FILES']
    img  = current_app.config['UPLOADED_IMG']
    root_path =''
    if extend in file:
        root_path = get_UPLOADED_FILES_DEST()
    elif extend in img:
        root_path = current_app.config['ROOT_PHYSICAL']
    # root_path = current_app.config['UPLOADED_FILES_DEST']
    # print(root_path)
    UrlPath = path.replace(root_path,'').replace('\\','/')
    return UrlPath

def URL2physical(path):
    # root_path = current_app.config['UPLOADED_FILES_DEST']
    extend = path.split('.')[-1]
    file = current_app.config['UPLOADED_FILES']
    img  = current_app.config['UPLOADED_IMG']
    root_path =''
    if extend in file:
        root_path = get_UPLOADED_FILES_DEST()
    elif extend in img:
        root_path = current_app.config['ROOT_PHYSICAL']
    if path.startswith('/'):
        path = path.lstrip('/')
    physical = os.path.join(root_path,path.replace('/','\\'))
    return physical

#--------------------文件上传出错------------------------------

def Removechar(string, char=';'):
    if string.endswith(char):
        return string.rstrip(char)



def make_path(basepath):
    '''
        生成日期组成的目录
        basepath: 为绝对路径。
    '''
    datearry = datetime.now().utctimetuple()
    datepath =r'{0}\{1}\{2}'.format(datearry[0],datearry[1],datearry[2])
    filepathdate = os.path.join(basepath,datepath)
    if not check_dir_file(filepathdate):
        os.makedirs(filepathdate)
    return filepathdate


def upload_file(file,changename=False,cover=False, fname=None):
    filepath = allowed_file(file.filename)
    if filepath:
        basepath = make_path(filepath)
        file_pre = file.filename.split('.')[0]
        filetype ='.'+ file.filename.split('.')[-1]
        filename = file_pre + filetype
        extend_num = 1
        
        if changename:
            filename = str(int(time.time())) + filetype

        if fname:
            filename = fname
        while True:
            if check_dir_file(os.path.join(basepath,filename)) and not cover:
                extend_name = '_%s' % str(extend_num)
                filename = file_pre + extend_name + filetype
                extend_num +=1
            else:
                break 
        try:
            file.save(os.path.join(basepath,filename))
        except Exception as e:
            raise ValueError('IO error')
        return physical2URL(os.path.join(basepath,filename))
    else:
        raise ValueError('Uploading this file is not allowed')


def upload_base64(filename, pre='1'):
    imgdata = filename
    etname = rt_base64_extand(filename)
    t = time.time()
    filename = pre + str(int(round(t * 1000))) + etname
    filepath = allowed_file(filename)
    if filename:
        basepath = make_path(filepath)
        try:
            quanpath = os.path.join(basepath,filename)
            data = imgdata.split(',')[1]
            image_data = base64.b64decode(data)
            with open(quanpath, 'wb') as f:
                f.write(image_data)
        except Exception as e:
            raise ValueError('IO error')
        return physical2URL(os.path.join(basepath,filename))
    else:
        raise ValueError('Uploading this file is not allowed')

def delfile(file):
    if file:
        physical = URL2physical(file)
        if check_dir_file(physical):
            os.remove(physical)
            return True
    return False


def rt_base64_extand(file):
    src = file
    datatype = src.split(',')[0]
    rs = re.search('^data:image/(?P<itype>[a-z]+);base64$',datatype)
    if rs:
        return '.' + rs.group('itype')
    return False


def searchfile(name,path1=r'i:'):
    allfiles = []
    allfiles.append(path1)
    while len(allfiles) != 0:
        path = allfiles.pop(0)
        if os.path.isdir(path):
            if os.path.basename(path) == 'System Volume Information' or os.path.basename(path) == '$RECYCLE.BIN':
                continue
            allfilepath = os.listdir(path)
            for line in allfilepath:
                newpath = path +'\\' + line
                allfiles.append(newpath)
        else:
            target = os.path.basename(path)
            if target == name:
                return path
    return -1




def hash_file_name(filename):
    fname = filename
    hs = hashlib.md5()
    hs.update(fname.encode(encoding='UTF-8'))
    return hs.hexdigest()




def create_config_file(configname, filename, dpsize, filesize,viewimg=[]):

    cfgname = configname
    config = configparser.ConfigParser()
    config['Default'] = {   'name': filename,
                            # 'dir': dname,
                            'size': filesize,
                            # 'ext': file.split('.')[-1],
                            'dpsize': dpsize,
                            'viewimg': viewimg
                            }
    with open(cfgname, 'w') as fr:
        config.write(fr)
    return config['Default']

    
#------------切割文件----------

def splitfile(mid,oldfile,hashfile,size=1024*1024*100):
    '''
    mid:任务队列id
    oldfile: 源文件路径
    hashfile:hash文件路径
    '''
    
    nfname = os.path.basename(hashfile)
    newdir = os.path.dirname(hashfile)
    filesize = os.path.getsize(oldfile)
    # filename = os.path.basename(oldfile)
    # imgpath = os.path.join(newdir,'ig',nfname)
    # viewimg = init_video_img(mid,oldfile,imgpath)
    # dictarr = create_config_file(hashfile, filename, size, filesize, viewimg)
    qe.put([mid,0,2])
    total = int(filesize)
    findex = 0 
    with open(oldfile,'rb') as fr:
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
            except IOError as e:
                break
    qe.put([mid,100,3])


def moveorcopy(app, vid, oldpath, fullname, move=True, status=None, perview=False):
    '''
    oldpath:源文件
    fullname目标文件
    status分割文件
    perview生成视频预览图
    move 移动文件
    '''
    with app.app_context():
        fname = os.path.basename(oldpath)
        mgmode = MessageList(
                name = fname,
                path = oldpath,
                zt = True,
                vid = vid
            )

        db.session.add(mgmode)
        db.session.commit()

        dirname = os.path.dirname(fullname)

        if not os.path.exists(dirname):
            os.makedirs(dirname)
        if status:
            nfname = os.path.basename(fullname)
            newdir = os.path.dirname(fullname)
            filesize = os.path.getsize(oldpath)
            filename = os.path.basename(oldpath)
            viewimg =''
            if perview:
                imgpath = os.path.join(newdir,'ig',nfname)
                viewimg = init_video_img(mid,oldpath,imgpath)
            dictarr = create_config_file(fullname, filename, (1024*1024*100), filesize, viewimg)
            splitfile(mgmode.vid,oldpath,fullname)
            os.remove(oldpath)
            
            qe.put([-1,'{0}文件分割完成'.format(oldpath)])
            db.session.delete(mgmode)
            db.session.commit()
        else:
            if oldpath != fullname:
                if move:
                    shutil.move(oldpath, fullname)
                # else:
                #     shutil.copy(oldpath, fullname)
                # shutil.move(oldpath, fullname)
                db.session.delete(mgmode)
                db.session.commit()
                qe.put([-1,'{0}文件移动完成'.format(oldpath)])



def movefile(vid,oldpath, filename,  move=True, status=None):
    '''
    oldpath:源文件绝对路径
    filename: 目标文件绝对路径
    movie: 是否保留文件
    status: 是否分割文件
    '''
    app=current_app._get_current_object()
    td = threading.Thread(target=moveorcopy, args=[app, vid, oldpath, filename, move, status])
    td.start()
        


def removevide(pypath, hashpath):
    if os.path.exists(pypath):
        os.remove(pyfile)
    if os.path.exists(hashpath):
        newdirpath = os.path.dirname(hashpath)
        if os.path.exists(newdirpath):
            shutil.rmtree(newdirpath)




def restorefile(vid,pypath, hashpath):
    '''
    pypath:目标路径
    hashpath: hash源文件
    '''

    app=current_app._get_current_object()

    td = threading.Thread(target=rsfile, args=[app,vid,pypath, hashpath])
    td.start()

def nrsfile(vid, pypath, hashpath,status=True):
    config = configparser.ConfigParser()
    config.read(hashpath)
    tatal = float(config['Default']['size'])
    dbsize = float(config['Default']['dpsize'])
    fname = os.path.basename(pypath)
    mgmode = MessageList(
                    name = fname,
                    path = pypath,
                    zt = False,
                    vid = vid
                )
    db.session.add(mgmode)
    db.session.commit()
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
            qe.put([mgmode.vid, pers])

    db.session.delete(mgmode)
    db.session.commit()
    qe.put([-1,'{0}整合完成'.format(pypath)])

def rsfile(app, vid, pypath, hashpath):
    with app.app_context():
        nrsfile(vid,pypath, hashpath)
    #     config = configparser.ConfigParser()
    #     config.read(hashpath)
    #     tatal = float(config['Default']['size'])
    #     dbsize = float(config['Default']['dpsize'])
    #     fname = os.path.basename(pypath)
    #     mgmode = MessageList(
    #                 name = fname,
    #                 path = pypath,
    #                 zt = False,
    #                 vid = vid
    #             )
    #     db.session.add(mgmode)
    #     db.session.commit()
    #     chumk = 0
    #     with open(pypath, 'wb') as fr:
    #         while True:
    #             try:
    #                 pdfile = hashpath + '{0}'.format(chumk)
    #                 source_file = open(pdfile,'rb')
    #                 fr.write(source_file.read())
    #                 source_file.close()
    #                 os.remove(pdfile)
    #             except IOError as e:
    #                 break
    #             chumk += 1
    #             pers = float(chumk*dbsize) / tatal
    #             pers = float('%.2f' % pers)
    #             if pers > 1:
    #                 pers = 1
    #             qe.put([mgmode.vid, pers])

    #     db.session.delete(mgmode)
    #     db.session.commit()
    #     qe.put([-1,'{0}整合完成'.format(pypath)])

def get_fs_info():
    tmplist = []
    pythoncom.CoInitialize ()
    c = wmi.WMI()
    for physical_disk in c.Win32_Volume():
        tmpdict = {}
        if physical_disk.DriveLetter:
            tmpdict["Caption"] = physical_disk.Caption
            tmpdict["DiskTotal"] = round(int(physical_disk.Capacity) / (1024 * 1024 * 1024), 2)
            tmpdict["DeviceID"] =re.findall('Volume{(.*?)}',physical_disk.DeviceID)[0]
            tmpdict["FileSystem"] = physical_disk.FileSystem
            tmpdict['SerialNumber'] = physical_disk.SerialNumber
            freesize = '%.1f' % (int(physical_disk.FreeSpace) / (1024*1024*1024))
            tmpdict['freesize'] = freesize
            tmplist.append(tmpdict)
    return tmplist


def cat2merger(mid,filename):
    hashfile = readfilePath(filename)
    num = 0 
    oldfile = ''
    config = configparser.ConfigParser()
    config.read(hashfile)
    tatal = float(config['Default']['size'])
    dbsize = float(config['Default']['dpsize'])
    while True:
        file = hashfile + str(num)
        if os.path.exists(file):
            break;
        num += 1
    pre_reader = 1024*1024*100*num
    if os.path.exists(filename):
        name = '_{0}'.format(os.path.basename(filename))

        oldfile = os.path.join(os.path.dirname(filename),name)
        os.rename(filename, oldfile)
    with open(filename,'w+b') as fr:
        pre_data = open(oldfile, 'rb')
        fr.write(pre_data.read(pre_reader))
        pre_data.close()
        os.remove(oldfile)
        while True:
            try:
                pdfile = hashfile + str(num)

                source_file = open(pdfile, 'rb')
                fr.write(source_file.read())
                source_file.close()
                os.remove(pdfile)
            except Exception as e:

                break

            num += 1
            pers = float(num*dbsize) / tatal
            pers = float('%.2f' % pers)
            if pers > 1:
                pers = 1
            qe.put([mid, pers])

            

def restore_thread(app,filename):
    with app.app_context():

        mgl = MessageList.query.filter_by(path=filename).first()

        if mgl:
            if mgl.zt:
                splitfile(mgl.id,filename, filename)
                os.remove(filename)
            else:
                cat2merger(mgl.id,filename)
            db.session.delete(mgl)
            db.session.commit()
            qe.put([-1,'{0}任务已恢复完毕'.format(mgl.name)])
            # os.path.exists

def restoretask(filename):
    if os.path.exists(filename):
        app=current_app._get_current_object()
        td = threading.Thread(target=restore_thread, args=[app,filename])
        td.start()


def perview_restorefile(vid,pypath,hashpath):
    app=current_app._get_current_object()
    td = threading.Thread(target=aysc_init_video_img, args=[app,vid,pypath,hashpath])
    td.start()

def aysc_init_video_img(app,vid,pypath,hashpath):
    with app.app_context():
        st = False
        if (not os.path.exists(pypath)) and os.path.exists(hashpath):
            nrsfile(vid, pypath, hashpath,status=False)
            st = True
        dirname = os.path.dirname(hashpath)
        bname = os.path.basename(hashpath)
        view_img_path = os.path.join(dirname,'ig')
        if not os.path.exists(view_img_path):
            os.makedirs(view_img_path)
        view_img = os.path.join(view_img_path,bname)
        view_list = init_video_img(vid,pypath,view_img)
        if not os.path.exists(hashpath):
            create_config_file(hashpath,os.path.basename(pypath),0,0,view_list)
        else:
            config = configparser.ConfigParser()
            config.read(hashpath)
            config['Default']['viewimg'] = str(view_list)
            with open(hashpath,'w') as fr:
                config.write(fr)
        if st:
            os.remove(pypath)

def get_video_msg(video):
    mglist = []
    if os.path.isfile(video):
        cap = cv2.VideoCapture(video)
        sceen = '{}*{}'.format(int(cap.get(3)), int(cap.get(4)))
        durtime = cap.get(7)/cap.get(5)
        mglist.append(sceen)
        mglist.append(durtime)
    return mglist


def aysc_init_zimu_img(vid, video, hashpath):
    app=current_app._get_current_object()
    td = threading.Thread(target=init_zimu_img, args=[app,vid, video, hashpath])
    td.start()


def init_zimu_img(app, vid, video, imgpath):
    with app.app_context():
        cap = cv2.VideoCapture(video)
        # fps = round(cap.get(5))
        fps = 1
        fpscount = int(cap.get(7))
        success ,frame = cap.read()
        i = 0
        j = 0
        img = None
        rows = 0
        coloums = 0
        time_start = time.time()
        while success:
            if ( i % fps ==0):
                filename =imgpath + r'\{}.jpg'.format(j)
                cv2.imwrite(filename,frame)
                persent = float((fps*(j+1))/fpscount)
                persent = float('%.2f' % persent)
                print('总帧数：', fpscount)
                print('以读帧数:',(fps*(j+1)))
                print(persent)
                qe.put([vid,persent,-1])
                j += 1
            success, frame = cap.read()
            i += 1
        time_end = (time.time() - time_start)
        print('==========================================', time_end,'============')


def time2int(strtime):
    tlist = strtime.split(':')
    h = int(tlist[0]) * 3600
    m = int(tlist[1])* 60
    s = int(tlist[2])
    return (h+m+s)






from ..models.movie import VideoFile
import os
import hashlib
from ..lib.diskdrive import Diskdrive
import cv2
from ..controller.diskcontroller import Diskcontroller
from ..controller.messagecontroller import MessageController
import threading
import shutil
import configparser
import json
import re
from .. import lock
import time

thread_status = False

class VideoFileController(object):

    def __init__(self,diskpart):
        self.diskpart = diskpart

    #创建VifeoFile类的对象
    def add_video_file(self, video, videopath):
        '''
        video: video对象
        videopath 文件物理路径
        '''
        if not os.path.exists(videopath):
            raise IOError(u'文件不存在')
        hashname = self.hash_file_name(videopath)
        if video.ismove:
            dc = Diskcontroller(self.diskpart)
            savepath = dc.get_default_path()
            print('默认磁盘路径:',savepath)
            # savepath = os.path.dirname(savepath)
            physical_path = '{}\\{}'.format(savepath.split(':')[-1],hashname)
        else:
            if video.splitfile:
                savepath = '{}\\{}'.format(os.path.dirname(videopath),hashname)
            else:
                savepath = os.path.dirname(videopath)
            physical_path = savepath.split(':')[-1]
        cap = cv2.VideoCapture(videopath)
        
        vfobj = VideoFile(
            name = os.path.basename(videopath),
            hashname = hashname,
            physical_path = physical_path,
            prew = video.perview,
            parting = video.splitfile,
            size = os.path.getsize(videopath),
            fps = round(cap.get(5)),
            crame_count = cap.get(7),
            durtime = int(cap.get(7)/cap.get(5)),
            width = cap.get(3),
            height = cap.get(4),
            ismove = video.ismove
            # part_uuid
        )
        dr = Diskdrive()
        caption = savepath.split('\\')[0]
        diskobj = dr.get_path_uuid(caption)
        if not diskobj:
            raise ValueError(u'找不到相应的磁盘')
        vfobj.part_uuid = diskobj.get('uuid')
        vfobj.vieo = video
        return vfobj

    #操作视频文件，生成图片或分割文件
    def __option_video_file(self, vfobj, sourcefile):
        if not isinstance(vfobj, VideoFile):
            raise ValueError(u'类型错误')
        caption = self.diskpart.get(vfobj.part_uuid,None)
        if caption is None:
                raise ValueError(u'找不到相应的磁盘')
        
        configpath = '{}{}'.format(caption,vfobj.get_config_dir())
        viewpath = '{}{}'.format(caption,vfobj.get_perview_dir())
        if vfobj.prew:
            self.create_preview(vfobj, sourcefile=sourcefile)
        if vfobj.parting:
            self.parting_file(vfobj, sourcefile)
        else:
            if vfobj.ismove:
                pypathdir = '{}{}'.format(caption, vfobj.physical_path)
                if not os.path.exists(pypathdir):
                    os.makedirs(pypathdir)
                pypath = '{}{}\\{}'.format(caption, vfobj.physical_path, vfobj.name)
                shutil.move(sourcefile, pypath)
          
    def __async_option_video_file(self,app,vfobj, sourcefile):
        with app.app_context():
            caption = self.diskpart.get(vfobj.part_uuid, None)
            if caption is None:
                raise ValueError(u'找不到磁盘')
            mgcontrol = MessageController()
            mgcontrol.put(
                    name = os.path.basename(sourcefile),
                    path = os.path.dirname(sourcefile),
                    zt = 0,
                    task = 0,
                    video_id= vfobj.video_id,
                    file_id = vfobj.id
            )
            global thread_status
            print('添加时lock.acquire()前状态:',thread_status)
            lock.acquire()
            print('添加时lock.acquire()后状态:',thread_status)
            if not thread_status:
                thread_status =True
                lock.release()
                self.__option_video_file(vfobj, sourcefile)
                mgcontrol.del_message_from_fileid(vfobj.id)
                self.op_all_queue()

            
    #使用线程异步执行操作文件
    def async_option_video_file(self,app,vfobj,sourcefile):
        td = threading.Thread(target=self.__async_option_video_file,args=[app,vfobj,sourcefile])
        td.start()

    def async_option_video_file_other(self, target, args):
        td = threading.Thread(target=target, args=args)
        td.start()

    #异步还原文件
    def async_restore_file(self, app, vfobj):
        with app.app_context():
            caption = self.diskpart.get(vfobj.part_uuid, None)
            if caption is None:
                raise ValueError(u'找不到磁盘')
            mgcontrol = MessageController()
            mgcontrol.put(
                    name = vfobj.name,
                    path = '{}{}'.format(caption, vfobj.physical_path),
                    zt = 0,
                    task = 3,
                    video_id= vfobj.video_id,
                    file_id = vfobj.id
            )
            global thread_status
            lock.acquire()
            
            if not thread_status:
                thread_status =True
                lock.release()
                self.restore_file(vfobj)
                mgcontrol.del_message_from_fileid(vfobj.id)
                self.op_all_queue()


    #还原视频文件
    def restore_file(self, vfobj):
        caption = self.diskpart.get(vfobj.part_uuid, None)
        if caption is None:
            raise ValueError(u'找不到磁盘')
        pypath = '{}{}\\{}'.format(caption, vfobj.physical_path, vfobj.name)
        hashpath = '{}{}\\{}'.format(caption, vfobj.physical_path, vfobj.hashname)

        vfobj.nrsfile(pypath, hashpath)


    #异步分割文件
    def async_parting_file(self, app, vfobj):
        with app.app_context():
            caption = self.diskpart.get(vfobj.part_uuid, None)
            if caption is None:
                raise ValueError(u'找不到磁盘')
            mgcontrol = MessageController()
            mgcontrol.put(
                    name = vfobj.name,
                    path = '{}{}'.format(caption, vfobj.physical_path),
                    zt = 0,
                    task = 2,
                    video_id= vfobj.video_id,
                    file_id = vfobj.id
            )
            global thread_status
            lock.acquire()
            if not thread_status:
                thread_status =True
                lock.release()
                self.parting_file(vfobj)
                mgcontrol.del_message_from_fileid(vfobj.id)
                self.op_all_queue()
            
    #分割视频文件
    def parting_file(self,vfobj, pypath=None):
        caption = self.diskpart.get(vfobj.part_uuid, None)
        if caption is None:
            raise ValueError(u'找不到磁盘')
        if pypath is None:
            pypath = '{}{}\\{}'.format(caption, vfobj.physical_path, vfobj.name)
        configpath = '{}{}'.format(caption, vfobj.get_config_dir())
        if not os.path.exists(configpath):
            os.makedirs(configpath)
        print(pypath)
        if not os.path.isfile(pypath):
            raise IOError(u'找不到源文件')
        self.create_config_file('{}\\{}'.format(configpath, vfobj.hashname),
                                        vfobj.name,
                                        (1024*1024*100),
                                        vfobj.size
        )
        hashpath = '{}{}\\{}'.format(caption, vfobj.get_config_dir(), vfobj.hashname)
        vfobj.splitfile(pypath, hashpath)
        # os.remove(pypath)

    #异步生成预览图
    def async_create_preview(self, app, vfobj):
        with app.app_context():
            caption = self.diskpart.get(vfobj.part_uuid, None)
            if caption is None:
                raise ValueError(u'找不到磁盘')
            mgcontrol = MessageController()
            mgcontrol.put(
                    name = vfobj.name,
                    path = '{}{}'.format(caption, vfobj.physical_path),
                    zt = 0,
                    task = 1,
                    video_id= vfobj.video_id,
                    file_id = vfobj.id
            )
            global thread_status
            lock.acquire()
            if not thread_status:
                thread_status =True
                lock.release()
                # self.parting_file(vfobj)
                self.create_preview(vfobj)
                mgcontrol.del_message_from_fileid(vfobj.id)
                self.op_all_queue()

    #生成视频预览图
    def create_preview(self, vfobj, sourcefile=None):
        
        caption = self.diskpart.get(vfobj.part_uuid, None)
        
        if caption is None:
            raise ValueError(u'找不到磁盘')

        if sourcefile is None:
            sourcefile = '{}{}'.format(caption, vfobj.pyurl)
        
        configpath = '{}{}'.format(caption,vfobj.get_config_dir())
        viewpath = '{}{}'.format(caption,vfobj.get_perview_dir())
        if not os.path.exists(viewpath):
                os.makedirs(viewpath)
        imgview = '{}\\{}'.format(viewpath, vfobj.hashname)
        #生成图片预览图
        viewimg = vfobj.init_video_img(sourcefile,imgview)

        #创建配置文件
        configfile = '{}\\{}'.format(configpath,vfobj.hashname)
        if not os.path.isfile(configfile):
            self.create_config_file('{}\\{}'.format(configpath, vfobj.hashname),
                                        vfobj.name,
                                        (1024*1024*100),
                                        vfobj.size,
                                        viewimg)
        else:
            config = self.read_config_file(configfile)
            config['Default']['viewimg'] = str(viewimg)
            with open(configfile, 'w') as fr:
                config.write(fr)



    #获取hash 名称
    def hash_file_name(self,filename):
        fname = filename
        hs = hashlib.md5()
        hs.update(fname.encode(encoding='UTF-8'))
        return hs.hexdigest()

    #创建配置文件
    def create_config_file(self,configname, filename, dpsize, filesize,viewimg=[]):
        config = configparser.ConfigParser()
        if not os.path.exists(configname):
            cfgname = configname
            
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
    #读取配置文件
    def read_config_file(self,filename):
        if not os.path.isfile(filename):
            raise IOError(u'配置文件不存在')
        config = configparser.ConfigParser()
        config.read(filename)
        return config

    #异步移除文件
    def async_remove_video_file(self, app, vfobj, status):
        with app.app_context():
            if status:
                self.del_video_file(vfobj)
            else:
                self.remove_video_file(vfobj)
    #从系统中移除视频，并删除电脑中的文件
    def del_video_file(self, vfobj):
        if not isinstance(vfobj, VideoFile):
            raise ValueError(u'类型错误')
        caption = self.diskpart.get(vfobj.part_uuid,None)
        if caption is None:
                raise ValueError(u'找不到相应的磁盘')
        if vfobj.parting or vfobj.prew:
            path = '{}\\{}'.format(caption,vfobj.physical_path)
            if os.path.exists(path):
                shutil.rmtree(path)
        else:
            videopath = '{}\\{}\\{}'.format(caption,vfobj.physical_path, vfobj.name)
            if os.path.exists(videopath):
                os.remove(videopath)
        # configpath = '{}\\{}'.format(caption, vfobj.get_config_dir())
        # if os.path.exists(configpath):
        #     shutil.rmtree(configpath)


    #在系统中移除视频，电脑保留该文件
    def remove_video_file(self, vfobj, tmpdir='L:\\tmp'):
        if not isinstance(vfobj, VideoFile):
            raise ValueError(u'类型错误')
        caption = self.diskpart.get(vfobj.part_uuid,None)
        if caption is None:
                raise ValueError(u'找不到相应的磁盘')
        if vfobj.parting:
            hashname = '{}{}\\{}'.format(caption,vfobj.physical_path.lstrip('\\'), vfobj.hashname)
            if vfobj.ismove:
                pyfile = '{}\\{}'.format(tmpdir, vfobj.name)
            else:
                pyfile = '{}\\{}\\{}'.format(caption,os.path.dirname(vfobj.physical_path), vfobj.name)
            #合并视频分片,保留到指定目录
            if not os.path.exists(tmpdir):
                os.makedirs(tmpdir)
            print(hashname)
            vfobj.nrsfile(pyfile, hashname)
        configpath = '{}\\{}'.format(caption, vfobj.get_config_dir())
        if os.path.exists(configpath):
            shutil.rmtree(configpath)


        

    #获取视频预览图，返回json数据
    def read_viewimg_json(self,vfobj):
        caption = self.diskpart.get(vfobj.part_uuid,None)
        if caption is None:
                raise IOError(u'找不到相应的磁盘')
        if vfobj.prew:
            configpath = '{}{}\\{}'.format(caption, vfobj.get_config_dir(),vfobj.hashname)
            config = configparser.ConfigParser()
            config.read(configpath)
            viewimg = config['Default'].get('viewimg',[])
            if viewimg:
                viewimg =eval(config['Default']['viewimg'])
                jsondict = {'data':viewimg}
                viewimg = json.dumps(jsondict)
            return viewimg
        return []

    #读取预览图
    def read_preview(self, vfobj, imgname):
        caption = self.diskpart.get(vfobj.part_uuid,None)
        if caption is None:
                raise ValueError(u'找不到相应的磁盘')
        # perview_dir = '{}{}'.format(caption, video.get_perview_dir())
        preview_path = '{}{}\\{}'.format(caption, vfobj.get_perview_dir(), imgname)
        if not os.path.isfile(preview_path):
            raise IOError(u'找不到相关文件')
        imgstream = ''
        with open(preview_path, 'rb') as fr:
            imgstream = fr.read()
        return imgstream

    #读取视频流
    def read_video_file_steam(self,vfobj, range_header):
        caption = self.diskpart.get(vfobj.part_uuid,None)
        if caption is None:
                raise ValueError(u'找不到相应的磁盘')
        if range_header :
            print(range_header)
            match = re.search(r'bytes=(\d+)-\d*', range_header)
            sk = int(match.group(1))
        else:
            sk = 0
        file = '{}{}'.format(caption, vfobj.pyurl)
        if vfobj.parting:
            config =configparser.ConfigParser()
            config.read(file)
            total = int(config['Default']['size'])
            dpsize = int(config['Default']['dpsize'])
            pdnum = int(sk / dpsize)
            local = int(sk % dpsize)
            localfile = file + str(pdnum)
        else:
            total = os.path.getsize(file)
            localfile = file
            local = sk
        with open(localfile, 'rb') as fr:
            fr.seek(local)
            chunk = fr.read(1024*1024*50)
            end = sk + len(chunk) -1
            bytesarry = 'bytes {}-{}/{}'.format(sk, end, total)
            headers = {
                'Accept-Ranges' : 'bytes',
                'Content-Type' : 'application/octet-stream',
                'Content-Range' : bytesarry
            }
            fr.close()
            return (chunk, 206, headers)


    def get_video_file_path(self,vfobj):
        caption = self.diskpart.get(vfobj.part_uuid,None)
        if caption is None:
                raise IOError(u'找不到相应的磁盘')
        return '{}{}'.format(caption, vfobj.pyurl)


    def op_all_queue(self):
        mgcontrol = MessageController()
        while True:
            mg = mgcontrol.get()
            if mg is None:
                lock.acquire()
                global thread_status
                thread_status = False
                lock.release()
                print('thread_status:', thread_status)
                break
            
            try:
                print('mg.file_id:', mg.file_id)
                count = 0
                while True:
                    # file = VideoFile.query.get(int(mg.file_id))
                    file = mgcontrol.get_file_id(mg.file_id)
                    if not file:
                        count += 1
                        print('执行第{}次重试'.format(count))
                        if count > 3:
                            raise ValueError(u'任务中的文件不存在')
                        
                        time.sleep(10)
                    else:
                        break
                sourcefile = '{}\\{}'.format(mg.path, mg.name)
                #0表示分割和预览
                if mg.task == 0:
                    self.__option_video_file(file, sourcefile)
                #1表示预览任务:
                if mg.task == 1:
                    self.create_preview(file,sourcefile=sourcefile)
                #2 表示分割任务
                if mg.task == 2:
                    self.parting_file(file,pypath=sourcefile)
                if mg.task == 3:
                    self.restore_file(file)
                mgcontrol.del_message_from_fileid(file.id)
            except Exception as e:
                print(str(e))
                mgcontrol.change(mg.id)
                continue


    def check_message(self, vfobj):
        caption = self.diskpart.get(vfobj.part_uuid,None)
        if caption is None:
            raise ValueError(u'找不到相应的磁盘')
        mgcontrol = MessageController()
        st = mgcontrol.check('{}{}\\{}'.format(
            caption, vfobj.physical_path, vfobj.name
            ))
        if st:
            return True
        return False




    

    
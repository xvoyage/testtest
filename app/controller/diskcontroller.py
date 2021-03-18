from ..models.disk import Diskdb
from datetime import datetime
from ..auth.forms import DiskForm
from ..lib.diskdrive import Diskdrive
import os
import wmi
import pythoncom
import re

class Diskcontroller(object):

    def __init__(self,diskpart):
        self.diskpart = diskpart


    #获取存储路径
    def get_default_path(self):
        # part = Diskdb.query.filter_by(Status=True).first()
        part = self.get_parting()
        if not part:
            raise 'err'
        part_id = self.diskpart.get(part.uuid,None)
        if not part_id:
            raise 'err'
        datearry = datetime.now().utctimetuple()
        datepath ='{}{}\\{}\\{}\\{}'.format(
            part_id.replace('\\',''),
            part.Path,
            datearry[0],
            datearry[1],
            datearry[2]
        )
        if not os.path.exists(datepath):
            os.makedirs(datepath)
        return datepath


    #获取容量最多的分区
    def get_parting(self):
        dr = Diskdrive()
        systemparts = dr.get_fs_info()
        parts = Diskdb.query.all()
        onlineparts = []
        for part in parts:
            for systempart in systemparts:
                if part.uuid == systempart['UUID']:
                    part.freesize = float(systempart['freesize'])
                    onlineparts.append(part)
                    break
        if not  onlineparts:
            return False
        newlist = sorted(onlineparts, key= lambda i : i.freesize, reverse=True)
        return newlist[0]
        

    #绑定数据
    def obj_bind(self, formdata):
        if not isinstance(formdata, DiskForm):
            raise ValueError(u'数据类型错误')
        part = formdata.part.data
        if not os.path.isdir(part):
            raise ValueError(u'输入文件路径错误')

        caption = part.split('\\')[0] + '\\'
        pythoncom.CoInitialize ()
        c = wmi.WMI()
        for physical_disk in c.Win32_Volume():
            print(physical_disk.Caption, caption)
            if physical_disk.Caption == caption:
                disk = Diskdb(
                    DiskTotal = round(int(physical_disk.Capacity) / (1024 * 1024 * 1024), 2),
                    uuid = re.findall('Volume{(.*?)}',physical_disk.DeviceID)[0],
                    Path = part.split(':')[-1].strip('\\'),
                    AliseName = formdata.alisename.data
                )
                return disk
        else:
            return False



    #显示分区列表
    def show_disk_list(self):
        dr = Diskdrive()
        diskdata = dr.get_fs_info()
        disks = Diskdb.query.all()
        for dk in disks:
            for rdisk in diskdata:
                uuid = rdisk['UUID']
                dk.FreeSize = None
                dk.Fullpath = None
                if uuid == dk.uuid:
                    dk.FreeSize = float(rdisk['freesize'])
                    dk.Fullpath = '{}\\{}'.format(self.diskpart.get(dk.uuid),dk.Path)
                    break
        return disks


        






    
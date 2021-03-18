from uuid import uuid4
import wmi
import os
import pythoncom
import re

class Diskdrive(object):
    def __init__(self):
        pass

    def __get_fs_info(self):
        tmplist = {}
        pythoncom.CoInitialize ()
        c = wmi.WMI()
        for physical_disk in c.Win32_Volume():
            if physical_disk.DriveLetter:
                key = physical_disk.Caption
                uuid = re.findall('Volume{(.*?)}',physical_disk.DeviceID)[0]
                tmplist[uuid] = key
        return tmplist

    def get_new_fs_info(self):
        tmplist = {}
        pythoncom.CoInitialize ()
        c = wmi.WMI()
        for physical_disk in c.Win32_Volume():
            if physical_disk.DriveLetter:
                key = physical_disk.Caption
                uuid = re.findall('Volume{(.*?)}',physical_disk.DeviceID)[0]
                tmplist[uuid] = key
        return tmplist


    @property
    def Drives(self):
        return self.__get_fs_info()

    @Drives.setter
    def Drives(self,value):
        raise 'err'


    def get_fs_info(self):
        tmplist = []
        pythoncom.CoInitialize ()
        c = wmi.WMI()
        for physical_disk in c.Win32_Volume():
            tmpdict = {}
            if physical_disk.DriveLetter:
                tmpdict["Caption"] = physical_disk.Caption
                tmpdict["DiskTotal"] = round(int(physical_disk.Capacity) / (1024 * 1024 * 1024), 2)
                tmpdict["UUID"] =re.findall('Volume{(.*?)}',physical_disk.DeviceID)[0]
                tmpdict["FileSystem"] = physical_disk.FileSystem
                # tmpdict['SerialNumber'] = physical_disk.SerialNumber
                freesize = '%.1f' % (int(physical_disk.FreeSpace) / (1024*1024*1024))
                tmpdict['freesize'] = freesize
                tmplist.append(tmpdict)
        return tmplist


    def get_path_uuid(self,caption):
        if not caption.endswith('\\'):
            caption  = caption + '\\'
        pythoncom.CoInitialize ()
        c = wmi.WMI()
        pathobj = {}
        for physical_disk in c.Win32_Volume():
            if physical_disk.Caption == caption:
                # disk = Diskdb(
                #     DiskTotal = round(int(physical_disk.Capacity) / (1024 * 1024 * 1024), 2),
                #     uuid = re.findall('Volume{(.*?)}',physical_disk.DeviceID)[0],
                #     # Path = part.split(':')[-1].strip('\\'),
                #     # AliseName = formdata.alisename.data
                # )
                pathobj['DiskTotal'] = round(int(physical_disk.Capacity) / (1024 * 1024 * 1024),2)
                pathobj['freesize'] = int(physical_disk.FreeSpace)
                pathobj['uuid'] = re.findall('Volume{(.*?)}',physical_disk.DeviceID)[0]

                return pathobj
        else:
            return False

    # def readuuid(self,tag):
    #     path = '{0}/data/config.cfg'.format(tag)
    #     if not os.path.exists(path):
    #         return False
    #     uuid = ''
    #     with open(path,'r') as fr:
    #         uuid = fr.readline()
    #     return uuid

    # def setuuid(self,tag):
    #     path = '{0}/data/config.cfg'.format(tag)
    #     if os.path.exists(path):
    #         return False
    #     uuid = str(uuid4())
    #     with open(path,'w') as fr:
    #         fr.write(uuid)
    #     return uuid
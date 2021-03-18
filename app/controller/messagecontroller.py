from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models.message import MessageList
from ..models import VideoFile
from  sqlalchemy.sql.expression import and_, func
import os

class MessageController(object):
    
    def __init__(self, connecttext=None):
        if connecttext is None:
            connecttext = 'mysql://root:samyshan@127.0.0.1/mcms?charset=utf8'
        self.engine = create_engine(connecttext)

    def check(self,filename):
        status = False
        print('check:',filename)
        path = os.path.dirname(filename)
        name = os.path.basename(filename)
        Dbsession = sessionmaker(bind=self.engine)
        dbsession = Dbsession()
        msg = dbsession.query(MessageList).filter(
            and_(
                    MessageList.path ==path,
                    MessageList.name == name
                )
            ).first()
        if msg:
            status = True
        dbsession.close()
        return status

    #获取信息列表中第一条信息，若没有返回空
    def get(self):
        msg = None
        Dbsession = sessionmaker(bind=self.engine)
        dbsession = Dbsession()
        msg = dbsession.query(MessageList).filter_by(zt=0).order_by(MessageList.id).first()
        if msg:
            # file_id = msg.id
            dbsession.refresh(msg)
            dbsession.expunge(msg)
        dbsession.close()
        return msg

    def change(self,fid):
        Dbsession = sessionmaker(bind=self.engine)
        dbsession = Dbsession()
        msg = dbsession.query(MessageList).get(int(fid))
        if msg:
            msg.zt = 1
            dbsession.add(msg)
            dbsession.commit()
        dbsession.close()

    #添加信息
    def put(self, name, path, zt, task, video_id, file_id):
        msg = MessageList(
            name = name,
            path = path,
            zt = zt,
            task = task,
            video_id = video_id,
            file_id = file_id
        )
        Dbsession = sessionmaker(bind=self.engine)
        dbsession = Dbsession()
        dbsession.add(msg)
        dbsession.commit()
        dbsession.close()

    #删除某条信息
    def del_message_from_fileid(self, id):
        status = False
        Dbsession = sessionmaker(bind=self.engine)
        dbsession = Dbsession()
        msg = dbsession.query(MessageList).filter_by(file_id=id).first()
        if msg:
            dbsession.delete(msg)
            dbsession.commit()
            status = True
        dbsession.close()
        return status

    def get_file_id(self,id):
        msg = False
        Dbsession = sessionmaker(bind=self.engine)
        dbsession = Dbsession()
        msg = dbsession.query(VideoFile).get(id)
        if msg:
            dbsession.refresh(msg)
            dbsession.expunge(msg)
        dbsession.close()
        return msg

    


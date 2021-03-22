# from .. import db
# # from ..lib.javdb import get_show_magnet, make_javdb_request
# from bs4 import BeautifulSoup
# from .. import qe
# # from flask import flash
# import threading

# class VdFollow(db.Model):
#     __tablename__ = 'vdfollow'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(64),nullable=False)
#     link = db.Column(db.String(256), nullable=False)
#     img = db.Column(db.String(256))
#     title = db.Column(db.String(512), nullable=False)
#     # __magnet = db.Column(db.String(1024))
#     status = db.Column(db.Boolean, default=False)

#     def __repr__(self):
#         return '<VdFollow %r>' % self.name

#     @property
#     def magnet(self):
#         # return ';'.join(self.__magnet)
#         return self.__magnet.split(';')

#     @property
#     def nlink(self):
#         return self.link.replace('https://javdb.com','/javdb')


#     def check_video(self,app):
#         with app.app_context():
#             vfs = VdFollow.query.filter_by(status=False).all()
#             if vfs:
#                 for vf in vfs:
#                     req = make_javdb_request(vf.link)
#                     if req is not None:
#                         bs = BeautifulSoup(req.text,'html.parser')
#                         mg = get_show_magnet(bs)
#                         if mg:
#                             vf.status = True
#                             db.session.add(vf)
#                             # flash('{}资源更新'.format(vf.name),'info')
#                             qe.put([-1,'{}资源更新了'.format(vf.name)])
#                 db.session.commit()
    
#     def async_check_video(self,app):
#         td =threading.Thread(target=self.check_video,args=[app])
#         td.start()





import os 
from app import create_app, db, socketio

from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
# from app.models import Actor, Category, Movie, Tag, User
from app.models import User, Category, Tag, Movie, VideoTime, ImgTag, Photo2Tag, Myphoto, Diskdb, Settings, MessageList, VdFollow

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
Migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, User=User,Category=Category, 
                    Tag=Tag, Movie=Movie, VideoTime=VideoTime)
    # return dict(app=app, db=db, Actor=Actor, Category=Category,
    #                 Movie=Movie, Tag=Tag, User=User)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
manager.add_command('run', socketio.run(app=app, host='192.168.1.127', port=80))


if __name__ == '__main__':
    manager.run()
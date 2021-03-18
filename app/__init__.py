from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from config import config
# from flask_uploads import UploadSet, ALL, IMAGES, configure_uploads, patch_request_class
from flask_ckeditor import CKEditor
from flask_socketio import SocketIO
from queue import Queue
from .lib.diskdrive import Diskdrive
import threading


login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
bootstrap = Bootstrap()
db = SQLAlchemy()
# mfile = UploadSet(extensions=['mp4','avi'])
ckeditor = CKEditor()
async_mode = None
socketio = SocketIO()
qe = Queue()
lock = threading.Lock()
# thread_status = False

disklist = Diskdrive().Drives


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    db.init_app(app)
    ckeditor.init_app(app)
    # configure_uploads(app, mfile)
    # patch_request_class(app, size=None)
    from .auth import auth as auth_blueprint
    from .main import main as main_blueprint
    from .imgview import img as img_blueprint
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(img_blueprint)
    socketio.init_app(app=app, async_mode=async_mode)
    return app
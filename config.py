import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    ROOT_PHYSICAL = os.path.join(basedir,'app')


    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    #SQLALCHEMY_DATABASE_URI =  os.environ.get('MYSQL_URI') or 'mysql://root:samyshan@localhost/cms'
    SQLALCHEMY_DATABASE_URI =  'mysql://root:samyshan@127.0.0.1/mcms'
    # UPLOADED_PHOTOS_DEST = r'D:\code\mcms\app\static\upload\image'
    UPLOADED_PHOTOS_DEST   = os.path.join(basedir,r'app\static\upload\image')
    # UPLOADED_FILES_DEST = r'J:\video'
    MAX_CONTENT_LENGTH = 210*1024*1024*1024
    UPLOADED_FILES = ['mp4','avi','mkv','wmv']
    UPLOADED_IMG = ['jpg','png','jpeg','gif']
    CKEDITOR_FILE_UPLOADER = 'auth.file_upload'
    CATEGORY_PER_PAGE = 30
    # COPY_FILE_DES = r'J:'
    # PARTITIONS = ['J:\\video','I:\\video','G:\\video','K:\\video']


config = {'development' : DevelopmentConfig, 'default' : DevelopmentConfig}
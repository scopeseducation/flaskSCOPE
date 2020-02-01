import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BASE_FOLDER = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.abspath(os.path.dirname(__file__)) + '/app/static'
    STATUS = ""
    CBS_STATUS = ""
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(UPLOAD_FOLDER, 'app.db')
    LOG_FOLDER = os.path.abspath(os.path.dirname(__file__)) + "/app/logs"
    EXT_SCRIPT_FOLDER = os.path.abspath(os.path.dirname(__file__)) + '/app/ext_scripts'
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'mp3', 'mp4'])

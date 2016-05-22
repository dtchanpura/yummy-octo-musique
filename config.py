import os

# from errors import *
# from mail_config import * # Mail Configs

basedir = os.path.abspath(os.path.dirname(__file__))

if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = ('sqlite:///' + os.path.join(basedir, 'app.db') +
                               '?check_same_thread=False')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SECRET_KEY = u'AV3#%$2SDvbW#BFNsdsba@2123wev'
TMP_FOLDER = os.path.join(basedir, 'tmp/')
SQLALCHEMY_TRACK_MODIFICATIONS = True
PORT = 8000
IP = '0.0.0.0'
APP_NAME = 'flaskapp'
HOST_NAME = 'localhost'

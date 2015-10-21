from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging.handlers import RotatingFileHandler
# import os

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
# env = Environment(loader=PackageLoader('app', 'templates'))
# mail = Mail(app)

file_handler = RotatingFileHandler('tmp/mplayer-be.log', 'a', 1 * 1024 * 1024, 10)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('music player backend startup')

from app import views, models

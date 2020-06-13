import os
basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True

db = 'sqlite:///' + os.path.join(basedir, 'storage.db')

#SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'storage.db')
#SQLALCHEMY_TRACK_MODIFICATIONS = True

SECRET_KEY = 'Driv3-1n-C@r!0c4-D3l!v3r7'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
from flask import Flask
#from flask_sqlalchemy import SQLAlchemy
#from flask_script import Manager
#from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)
app.config.from_object('config')
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#db = SQLAlchemy(app)
#migrate = Migrate(app, db)

#manager = Manager(app)
#manager.add_command('db', MigrateCommand)

# Comentar esse trecho, caso não seja a primeira vez
#from app.models import tables, dataManipulation
from app.controllers import default
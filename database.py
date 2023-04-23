from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:QlWuEkRa@localhost:5432/ur_db_dev'
db = SQLAlchemy(app)

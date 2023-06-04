from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'QlWuEkRa')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST', '31.131.17.213')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT', '5432')
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'luka')
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'ur_db_dev')


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:POSTGRES_PASSWORD@POSTGRES_HOST:POSTGRES_PORT/POSTGRES_DB'
db = SQLAlchemy(app)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import redis

POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'QlWuEkRa')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST', '31.131.17.213')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT', '5432')
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'luka')
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'ur_db_dev')

REDIS_BIND = os.environ.get('REDIS_BIND')
REDIS_PORT = os.environ.get('REDIS_PORT')

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
app.config['REDIS_URL'] = f'redis://{REDIS_BIND}:{REDIS_PORT}'

db = SQLAlchemy(app)
rdb = redis.Redis.from_url(app.config['REDIS_URL'])

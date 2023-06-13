from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import dotenv_values, load_dotenv
import redis
import os

env_vars = dotenv_values()
POSTGRES_HOST = env_vars['POSTGRES_HOST']
POSTGRES_PASSWORD = env_vars['POSTGRES_PASSWORD']
POSTGRES_PORT = env_vars['POSTGRES_PORT']
POSTGRES_USER = env_vars['POSTGRES_USER']
POSTGRES_DB = env_vars['POSTGRES_DB']

REDIS_BIND = env_vars['REDIS_BIND']
REDIS_PORT = env_vars['REDIS_PORT']

# load_dotenv()
# POSTGRES_HOST = os.getenv('POSTGRES_HOST')
# POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
# POSTGRES_PORT = os.getenv('POSTGRES_PORT')
# POSTGRES_USER = os.getenv('POSTGRES_USER')
# POSTGRES_DB = os.getenv('POSTGRES_DB')
#
# REDIS_BIND = os.getenv('REDIS_BIND')
# REDIS_PORT = os.getenv('REDIS_PORT')


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
app.config['REDIS_URL'] = f'redis://{REDIS_BIND}:{REDIS_PORT}'

db = SQLAlchemy(app)
rdb = redis.Redis.from_url(f'redis://{REDIS_BIND}:{REDIS_PORT}')
